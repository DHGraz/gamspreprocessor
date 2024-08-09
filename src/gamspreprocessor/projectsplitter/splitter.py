from pathlib import Path
import re
import shutil
from typing import Dict, Union
import xml.etree.ElementTree as ET
import os
import mimetypes
from .bookkeeper import BookKeeper
from uritools import urisplit
# Match Namespaces to formats
XML_FORMATS = {
    "http://www.tei-c.org/ns/1.0": "tei",
    "http://www.lido-schema.org": "lido",
}

def guess_format(filename: str) -> str:
    """Guess the format of the file from the extension.

    It does more than the mimetype guesser, as it also checks the namespaces for xml files.
    All string returned are lowercase.
    """
    mtype = mimetypes.guess_type(filename)[0]
    file_format = None
    if mtype == 'application/xml':
        file_format = "xml"  # for xml without namespace
        for node in ET.iterparse(filename, events=["start-ns"]):
            file_format = XML_FORMATS.get(node[1][1], "xml")
            break
    elif mtype.startswith('application/'):
        file_format = mtype.split('/')[1]
    elif mtype.startswith('text/'):
        file_format = mtype.split('/')[1]
    else:
        file_format = mtype.split('/')[0]
    return file_format.lower()
    

def validate_filename(path:Path) -> None:
    "Raise a ValueError if filename does not match our conventions."
    allowed_pattern = '^([a-z]:)?[.-_a-z0-9]+$'
    filename = path.name
    m = re.match(allowed_pattern, filename)
    if m is None:
        raise ValueError(f"Filename {filename} does not match the allowed pattern {allowed_pattern}")

def extract_pid(path:Path) -> str:
    "Extract pid from a path."
    return ".".join(path.name.split('.')[0:-1])

def get_namespaces(filename: Path) -> Dict[str, str]:
    "Return all namespaces from the XML file a dictionary."
    return {k:v for (_, (k, v)) in ET.iterparse(filename, events=["start-ns"])}

def register_namespaces(namespaces: dict) -> None:
    "Register all namespaces in the ElementTree module."
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])


def rank_path(short_path:Path, long_path:Path):
    "Return how many chars are the same at the end of both paths."
    score = 0

    for short, long in zip(str(short_path)[::-1], str(long_path)[::-1]):
        if short == long:
            score += 1
        else:
            break
    return score


def find_file(referenced_uri: str, source_dir: Path) -> Union[Path, None]:
    """Try to find a file below source_dir with might match the file referenced in uri.
    
    The file will be identified by the best matching path (dir + filename)
    If 2 or more paths are ranked equally, the shortest matching path will be returned.
    
    Return path to the first file which matches or None if no file was found
    """
    uri = urisplit(referenced_uri)
    path = uri.path
    if path.endswith('/'):
        path = path[:-1]
    
    ranked_paths = []
    for file in source_dir.rglob(path.split('/')[-1]):
        ranked_paths.append((rank_path(path, file), file))

    if ranked_paths:
        # we sort by 1) rank (desc) and 2) length of the path (asc: *-1) 
        ranked_paths.sort(key=lambda x: (x[0], len(str(x[1])*-1)), reverse=True)
        return ranked_paths[0][1]
    return None

class ObjectDirectory:
    "Class to handle a directory for a generic single object."

    def __init__(self, path:Path):
        """Initialize the object directory.
        
        File will be created, if necessary.
        """
        self.path = path
        if self.path.is_dir():
            # TODO: How to react if the directory exists and is not empty?
            pass
        else:
            self.path.mkdir()
        self.files = []


    def split(self, sourcefile:Path):
        "Copy the sourcefile to the object directory."
        shutil.copy(sourcefile, self.path)
        self.files.append(sourcefile)


class TEIObjectDirectory(ObjectDirectory):
    
    def split(self, sourcefile: Path):
        "Copy the sourcefile and all referenced files to the object directory."
        referenced_files = set()  # all referenced files must be copied, 
        
        #source_dir = sourcefile.parent
        shutil.copy(sourcefile, self.path)
        self.files.append(sourcefile)

        
        new_sourcefile = self.path / sourcefile.name

        # we want the keep the original prefixes in the namespaces
        register_namespaces(get_namespaces(new_sourcefile))
        
        tree = ET.parse(new_sourcefile)
        root = tree.getroot()
        self._replace_graphics(root, sourcefile.parent, referenced_files)
        # TODO: can we make this more generic?
        # for graphic in root.findall(".//{http://www.tei-c.org/ns/1.0}graphic"): # TODO: tei:?
        #     src_file, new_image_name = fix_image_url(
        #         graphic.attrib["url"],
        #         sourcefile.parent,
        #         graphic.attrib.get("{http://www.w3.org/XML/1998/namespace}id", ""),
        #     )
        #     if new_image_name is not None:
        #         graphic.set("url", f"./{new_image_name}")
        # #         ref_files.add((src_file, target_dir / new_image_name))

        # tree.write(target_dir / source_file.name, encoding="utf-8", xml_declaration=True)
        # # we copy the images after writing the TEI file (just in case something goes wrong)
        # for original_url, new_url in ref_files:
        #     logger.debug("Moving %s to %s", original_url, new_url)
        #     os.rename(original_url, target_dir / new_url)


    def _replace_graphics(self, root_node: ET.Element, source_dir:Path, referenced_files:set) -> None:
        "Replace the graphic elements in the tree."

        for graphic in root_node.findall(".//{http://www.tei-c.org/ns/1.0}graphic"):  # TODO: should also work with tei:
            referenced_uri = graphic.attrib["url"]
            graphic_id = graphic.attrib.get("{http://www.w3.org/XML/1998/namespace}id", "")
            referenced_file = find_file(referenced_uri, source_dir)        

            if referenced_file is not None:
                # if an id is set. we use the id as file name, not the original name
                new_image_name = f"{graphic_id}.{referenced_file.suffix}"
                graphic.set("url", f"./{new_image_name}")
                referenced_files.add(referenced_file)



            #src_file, new_image_name = fix_image_url(
            #    graphic.attrib["url"],
            #    sourcefile.parent,
            #    graphic.attrib.get("{http://www.w3.org/XML/1998/namespace}id", ""),
            #)
            #if new_image_name is not None:
            #    graphic.set("url", f"./{new_image_name}")
            #    ref_files.add((src_file, target_dir / new_image_name))

class LIDOObjectDirectory(ObjectDirectory):
    pass


class ProjectSplitter:

    def __init__(self, outputdir: Path):
        self.outputdir = outputdir
        if not self.outputdir.exists():
            self.outputdir.mkdir()
        self._bookkeeper = BookKeeper(self.outputdir)

    def split(self, sourcefile: Path, objecttype: str) -> None:
        validate_filename(sourcefile)
        pid = extract_pid(sourcefile)
        if objecttype == "auto":
            objecttype = guess_format(sourcefile)

        if objecttype == "tei":
            objdir = TEIObjectDirectory(self.outputdir / pid)
            #self._create_tei_object_dir(sourcefile, pid)
        elif objecttype == "lido":
            objdir = LIDOObjectDirectory(self.outputdir / pid)
            #self._create_lido_object_dir(sourcefile, pid)
        else:
            objdir = ObjectDirectory(self.outputdir / pid)
            #raise ValueError(f"Unknown object type {objecttype}")
        objdir.split(sourcefile)
        for path in objdir.files:
            self._bookkeeper.consumed(path)

#     # TODO: validate file name
#     pid = os.path.splitext(filename)[0]
#     if object_type == "auto":
#         object_type = guess_format(source_file)
#         if object_type == "TEI":
#             self._create_tei_object_dir(source_file, target_root / pid)
#         elif object_type == "LIDO":
#             self._create_lido_object_dir(source_file, target_root / pid)
#         else:
#             # TODO: do we need more formats?
#             # TODO:: How can generic formats be handled?
#             raise ValueError(f"Unknown object type {object_type}")

#     # images = extract_images(source_file)
#     print(source_file, filename, pid)
# #             sourcefile = Path(sourcefile)
# #             create_object_dir(sourcefile, target_dir, args.format)
# #             bookkeeper.consumed(sourcefile)
# #             object_counter += 1
# #             unhandled_files = bookkeeper.get_unhandled()
    

    def reset(self) -> None:
        "Reset the bookkeeper."
        self._bookkeeper.reset()

    def _create_tei_object_dir(self, sourcefile: Path, pid: str) -> None:
        "Copy a TEI file and all referenced images (and other files) to a new directory"
        target_dir = self.outputdir / pid
        target_dir.mkdir()
        ref_files = set()  # all referenced files must be copied, too

        # we want the keep the original prefixes in the namespaces
        register_namespaces(get_namespaces(sourcefile))
        
        tree = ET.parse(sourcefile)
        root = tree.getroot()
        # TODO: can we make this more generic?
        for graphic in root.findall(".//{http://www.tei-c.org/ns/1.0}graphic"): # TODO: tei:?
            src_file, new_image_name = fix_image_url(
                graphic.attrib["url"],
                sourcefile.parent,
                graphic.attrib.get("{http://www.w3.org/XML/1998/namespace}id", ""),
            )
            if new_image_name is not None:
                graphic.set("url", f"./{new_image_name}")
                ref_files.add((src_file, target_dir / new_image_name))

        tree.write(target_dir / source_file.name, encoding="utf-8", xml_declaration=True)
        # we copy the images after writing the TEI file (just in case something goes wrong)
        for original_url, new_url in ref_files:
            logger.debug("Moving %s to %s", original_url, new_url)
            os.rename(original_url, target_dir / new_url)