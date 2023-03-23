""" Main settings for the application"""
import logging
import os

POSTGRES_HOST = (
    os.environ["POSTGRES_HOST"]
    if os.environ.get("POSTGRES_HOST") is not None
    else "localhost"
)
POSTGRES_DB = (
    os.environ["POSTGRES_DB"]
    if os.environ.get("POSTGRES_DB") is not None
    else "scrapDb"
)
POSTGRES_USER = (
    os.environ["POSTGRES_USER"]
    if os.environ.get("POSTGRES_USER") is not None
    else "scrapReality"
)
POSTGRES_PASSWORD = (
    os.environ["POSTGRES_PASSWORD"]
    if os.environ.get("POSTGRES_PASSWORD") is not None
    else "Password001+"
)

POSTGRES_PORT = (
    int(os.environ["POSTGRES_PORT"])
    if os.environ.get("POSTGRES_PORT") is not None
    else 5432
)
levels = {"DEBUG": logging.DEBUG, "NOTSET": logging.NOTSET, "INFO": logging.INFO,
          "WARNING": logging.WARNING, "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}
try:
    logging_str = str(os.environ["LOGGING_LEVEL"]).upper() if os.environ.get("LOGGING_LEVEL") is not None else "INFO"
    LOGGING_LEVEL = levels[logging_str]
except KeyError:
    LOGGING_LEVEL = logging.INFO

SUPPORTED_PROPORTIONS = {
    "1+kk": "1+kk",
    "2+kk": "2+kk",
    "3+kk": "3+kk",
    "4+kk": "4+kk",
    "5+kk": "5+kk",
    "1+1": "1+1",
    "2+1": "2+1",
    "3+1": "3+1",
    "4+1": "4+1",
    "5+1": "5+1",
    "atypické": "atypicky",
    "6": "6-a-vice",
}


def get_logger(module: str) -> logging.Logger:
    """
    Get logger with settings for the current module
    """
    logger = logging.getLogger(module)
    logger.setLevel(LOGGING_LEVEL)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
