# stdlib imports
import logging
import sys


def configure():
    """Configure logging for CLI use.

    This configures logging to go stdout by default and to only include the raw
    message in the output (no decoration).

    This configuration is CLI specific and other users of this library may
    choose to configure logging in a different way that's more appropriate for
    the use case (e.g. JSON output for server-side logging).
    """
    FORMAT_STRING = "%(message)s"
    LEVEL = logging.INFO
    STREAM = sys.stdout

    root_logger = logging.getLogger()
    handler = logging.StreamHandler(stream=STREAM)

    handler.setFormatter(logging.Formatter(FORMAT_STRING))
    root_logger.addHandler(handler)
    root_logger.setLevel(LEVEL)
