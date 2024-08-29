"""Utility function for the gamspreprocessor package."""

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from . import NAME

logger = logging.getLogger(NAME)


def configure_logging(
    log_level: int = logging.INFO, logfile: str = None, logfile_level=logging.INFO
) -> None:
    """Configure the logging module.

    I prefer to use a common logger for all modules in the package. So this function should
    be called once in the main module of the package.
    """
    logger.setLevel(log_level)

    ch = logging.StreamHandler()
    ch_formatter = logging.Formatter("%(message)s")
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)

    if logfile:
        fh = logging.FileHandler(logfile)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(file_formatter)
        fh.setLevel(logfile_level)
        logger.addHandler(fh)


def register_namespaces(namespaces: dict) -> None:
    "Register all namespaces in the ElementTree module."
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])


def get_namespaces(filename: Path) -> dict[str, str]:
    "Return all namespaces from the XML file a dictionary."
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
