"""Utility function for the gamspreprocessor package."""

import logging
import re
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)


def configure_logging(
    log_level: int = logging.INFO,
    logfile: str = "",
    logfile_level: int = logging.INFO,
) -> logging.Logger:
    """Configure the root logger.

    Args:
        log_level: The log level for the console.
        logfile: The filename for the log file. If not provided, no log file will be created.
        logfile_level: The log level for the log file.
    """
    logging.basicConfig(level=log_level)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

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
    return root_logger


def register_namespaces(namespaces: dict) -> None:
    """Register all namespaces in dict `namespaces` for the ElementTree module.

    Calling this function will make sure that the namespaces are available
    during serialization ti avoid namespace prefixes like `ns0` or `ns1`.
    """
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])


def get_namespaces(filename: Path) -> dict[str, str]:
    """Return all namespaces with prefixes from the XML file as dictionary."""
    return {k: v for (_, (k, v)) in ET.iterparse(filename, events=["start-ns"])}


def validate_pid(pid: str) -> None:
    "Raise a ValueError if pid does not match our conventions."
    allowed_pattern = r"^([a-zA-Z]+:)?[a-zA-Z0-9-._]+$"

    m = re.match(allowed_pattern, pid)
    if m is None:
        raise ValueError(
            f"PID {pid} does not match the allowed pattern {allowed_pattern}"
        )
    if ":" in pid:
        warnings.warn(
            f"PID {pid} contains a colon, which is discouraged in the new GAMS.",
            UserWarning,
        )


def find_multiple_files_per_dir(paths: list[Path]) -> list[tuple[Path, list[Path]]]:
    """Find multiple files in each directory matching a pattern.

    Args:
        paths: A list of files.
    Returns:
        A list of tuples (dirname, files) for all directories containing multiple files.
    """
    multi_file_dirs: dict[str, dict[str, Path]] = {}
    # collect parent dirs
    for path in paths:
        containing_dir: str = str(path.parent)
        path_files = multi_file_dirs.get(containing_dir, [])
        path_files.append(path)
        multi_file_dirs[containing_dir] = path_files

    prolematic_dirs = []
    for dir, files in multi_file_dirs.items():
        if len(files) > 1:
            files.sort()
            prolematic_dirs.append((Path(dir), files))
    prolematic_dirs.sort(key=lambda x: x[0])
    return prolematic_dirs
