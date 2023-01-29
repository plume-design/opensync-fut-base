import logging
import sys
import types

LOGR_ATTR = 'futgroup'
LOGR_FMT = '%(asctime)s %(levelname)s %(futgroup)s %(message)s'
LOGR_FMT_DEBUG = '%(asctime)s %(levelname)s %(futgroup)s [%(module)s:%(funcName)s %(lineno)d]: %(message)s'
LOGR_DATEFMT = '%H:%M:%S'
LOGR_NAME = 'FUT'
LOGR_GROUP = '[FRM]'
LOGR_LEVEL = logging.INFO
LOGR_LEVEL_DEBUG = logging.DEBUG
LOGR_DBG = '--dbg' in sys.argv
if LOGR_DBG:
    LOGR_LEVEL = LOGR_LEVEL_DEBUG
    LOGR_FMT = LOGR_FMT_DEBUG

# Define 4-letter abbreviations to logging levels used by logging library
logging.addLevelName(logging.CRITICAL, "CRIT")
logging.addLevelName(logging.ERROR, "ERR ")
logging.addLevelName(logging.WARNING, "WARN")
logging.addLevelName(logging.INFO, "INFO")
logging.addLevelName(logging.DEBUG, "DBG ")

fut_logger = logging.getLogger(LOGR_NAME)
fut_logger.setLevel(LOGR_LEVEL)
fut_logger.propagate = False


class FutLoggerAdapter(logging.LoggerAdapter):
    """Wrap LoggerAdapter with value for extra={'futgroup': 'value'}.

    Value is inserted into log record in place of %(futgroup)s
    Example of use:
        logger = logging.getLogger(LOGR_NAME)
        adapter = FutLoggerAdapter(logger, {LOGR_ATTR: GROUP_NAME})
    Defaults:
        logger=fut_logger
        extra={'futgroup': '[FRM]'}
    """

    def __init__(self, logger=fut_logger, extra=types.MappingProxyType({LOGR_ATTR: LOGR_GROUP})):
        if not all([isinstance(extra, dict), LOGR_ATTR in extra]):
            extra = {LOGR_ATTR: LOGR_GROUP}
        super(FutLoggerAdapter, self).__init__(logger, extra)
        print(f'### INITIALIZING LOGGER, DEBUG:{LOGR_DBG}')
        # Determine logging level and format
        logger.setLevel(LOGR_LEVEL)
        # create console handler
        stream_hdlr = logging.StreamHandler()
        stream_hdlr.setLevel(LOGR_LEVEL)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(LOGR_FMT, LOGR_DATEFMT)
        stream_hdlr.setFormatter(formatter)
        logger.addHandler(stream_hdlr)


_fut_adapter = None


def get_logger():
    """Instantiate the global adapter (once)."""
    global _fut_adapter
    if _fut_adapter is None:
        _fut_adapter = FutLoggerAdapter(logger=fut_logger, extra={LOGR_ATTR: LOGR_GROUP})
    return _fut_adapter


"""
Boilerplate convenience methods for logging.LoggerAdapter class:
def debug(self, msg, *args, **kwargs):
def info(self, msg, *args, **kwargs):
def warning(self, msg, *args, **kwargs):
def warn(self, msg, *args, **kwargs):
def error(self, msg, *args, **kwargs):
def exception(self, msg, *args, exc_info=True, **kwargs):
def critical(self, msg, *args, **kwargs):
"""
