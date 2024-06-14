import logging

logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)

stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)

logger.addHandler(stream)