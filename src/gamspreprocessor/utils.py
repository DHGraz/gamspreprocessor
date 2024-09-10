"""Utility function for the gamspreprocessor package."""

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)

def configure_logging(
    log_level: int = logging.INFO, logfile: str = None, logfile_level=logging.INFO
) -> None:
    """Configure the root logger.

    Args:
        log_level: The log level for the console.
        logfile: The filename for the log file. If not provided, no log file will be created. 
        logfile_level: The log level for the log file.
    """
    logging.basicConfig(level=log_level)
    root_logger = logging.getLogger()

    ch = logging.StreamHandler()
    ch_formatter = logging.Formatter("%(message)s")
    ch.setFormatter(ch_formatter)
    root_logger.addHandler(ch)

    if logfile:
        fh = logging.FileHandler(logfile)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(file_formatter)
        fh.setLevel(logfile_level)
        root_logger.addHandler(fh)


def register_namespaces(namespaces: dict) -> None:
    """Register all namespaces in dict `namespaces` for the ElementTree module.

    Calling this function will make sure that the namespaces are available 
    during serialization ti avoid namespace prefixes like `ns0` or `ns1`.
    """
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])


def get_namespaces(filename: Path) -> dict[str, str]:
    """Return all namespaces with prefixes from the XML file as dictionary.
    """
    return {k: v for (_, (k, v)) in ET.iterparse(filename, events=["start-ns"])}


def validate_filename(path: Path) -> None:
    "Raise a ValueError if filename does not match our conventions."
    allowed_pattern = r"^([a-zA-Z]+:)?[a-zA-Z0-9-._]+$"
    filename = path.name
    m = re.match(allowed_pattern, filename)
    if m is None:
        raise ValueError(
            f"Filename {filename} does not match the allowed pattern {allowed_pattern}"
        )
    if ':' in filename:
        logger.warning("Filename %s contains a colon, which is discouraged in the new GAMS.", filename)
        
