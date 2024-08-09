"""Function to split GAMS files into project folders."""

from pathlib import Path

import logging

import os
import xml.etree.ElementTree as ET
import json
from .bookkeeper import BookKeeper

# # Match Namespaces to formats
# XML_FORMATS = {
#     "http://www.tei-c.org/ns/1.0": "TEI",
#     "http://www.lido-schema.org": "LIDO",
# }

logger = logging.getLogger("make_folders")
bookkeeper = None


# def get_namespaces(filename) -> dict:
#     "Return all namespaces from the XML file a dictionary."
#     return {k:v for (_, (k, v)) in ET.iterparse(filename, events=["start-ns"])}

# def register_namespaces(namespaces: dict):
#     "Register all namespaces in the ElementTree module."
#     for ns in namespaces:
#         ET.register_namespace(ns, namespaces[ns])


def uri_to_filename(uri) -> str:
    "Extract the last part of uri (i.e. the filename)."
    path = uri.split("://")[-1]
    return os.path.basename(path)


# TODO: maybe this should be more general (eg. search for url=?)
# this could be ref, link, target etc.
def fix_image_url(uri: str, img_dir: Path, xmlid: str = "") -> tuple[str, str]:
    """Find a fitting image file for uri in or below img_path.

    * URIs with file:// as schema are expected to exist in img_dir or a folder below img_dir.
      In this case the return value is a tuple with the source file (potentially with path)
      and the name of the target file. The target file is the name of the image file or
      the value of xml:id if present.
    * URIs with http(s) schema are expected to be external images. But still we try to find
      a matching image below img_dir, as people tend to be creative with uris. 
      If we find one, we return the relative path to the image, if not, target is None.
    """
    img_name = uri_to_filename(uri)  # the name of the image file
    real_img = None  # the real image file with relative path
    for file in img_dir.rglob(img_name):
        real_img = str(file)
        break
    if real_img is None:  # we did not find a fitting image below img_dir
        if uri.startswith("http"):  # It seem the uri is referencing an external image
            source_file = uri
            target_file = None
        else:
            # If image is not references with a http(s) schema, we assume it is a missing local file
            logger.error("Image %s not found in %s or below", img_name, img_dir)
            raise FileNotFoundError(f"Image {img_name} not found in {img_dir} or below")
    else:
        source_file = str(real_img)
        target_file = img_name
        if xmlid:
            target_file = xmlid
    return source_file, target_file


# def guess_format(filename: str) -> str:
#     "Guess the format of the file from the extension."
#     ext = os.path.splitext(filename)[1]
#     if ext == ".xml":
#         # [node for _, node in ET.iterparse(filename, events=['start-ns'])]
#         for node in ET.iterparse(filename, events=["start-ns"]):
#             file_format = XML_FORMATS.get(node[1][1], "XML")
#             break
#         return file_format
#     raise ValueError(f"Unknown format for file {filename}")


# def create_tei_object_dir(source_file: Path, target_dir: Path):
#     "Copy a TEI file and all referenced images to a new directory."
#     target_dir.mkdir()

#     images = set()
#     register_namespaces(get_namespaces(source_file))
#     print(get_namespaces(source_file))
#     tree = ET.parse(source_file)
#     root = tree.getroot()
#     for graphic in root.findall(".//{http://www.tei-c.org/ns/1.0}graphic"):
#         src_file, new_image_name = fix_image_url(
#             graphic.attrib["url"],
#             source_file.parent,
#             graphic.attrib.get("{http://www.w3.org/XML/1998/namespace}id", ""),
#         )
#         if new_image_name is not None:
#             graphic.set("url", f"./{new_image_name}")
#             images.add((src_file, target_dir / new_image_name))

#     tree.write(target_dir / source_file.name, encoding="utf-8", xml_declaration=True)
#     # we copy the images after writing the TEI file (just in case something goes wrong)
#     for original_url, new_url in images:
#         logger.debug("Moving %s to %s", original_url, new_url)
#         os.rename(original_url, target_dir / new_url)


# def create_lido_object_dir(source_file: Path, target_dir: Path):
#     "Copy a LIDO file and all referenced images to a new directory"
#     # TODO


def create_object_dir(source_file: Path, target_root: Path, object_type: str):
    "Convert a single file."
    filename = os.path.basename(source_file)
    # TODO: validate file name
    pid = os.path.splitext(filename)[0]
    if object_type == "auto":
        object_type = guess_format(source_file)
        if object_type == "TEI":
            create_tei_object_dir(source_file, target_root / pid)
        elif object_type == "LIDO":
            create_lido_object_dir(source_file, target_root / pid)
        else:
            # TODO: do we need more formats?
            # TODO:: How can generic formats be handled?
            raise ValueError(f"Unknown object type {object_type}")

    # images = extract_images(source_file)
    print(source_file, filename, pid)


# def main(
#         *args: str,
#     target_dir: str, file_format: str, reset_bookkeep=False,
# ) -> tuple[int, list[Path]]:
#     "Main function to split a project into individual object directories."
#     target_dir = Path(target_dir)
#     global bookkeeper

#     object_counter = 0
#     with BookKeeper(target_dir) as bookkeeper:
#         if reset_bookkeep:
#             bookkeeper.reset()
#         for sourcefile in args:
#             sourcefile = Path(sourcefile)
#             create_object_dir(sourcefile, target_dir, args.format)
#             bookkeeper.consumed(sourcefile)
#             object_counter += 1
#             unhandled_files = bookkeeper.get_unhandled()
#     return object_counter, unhandled_files
