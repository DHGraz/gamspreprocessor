"""Utility function for the gamspreprocessor package."""

import logging

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
