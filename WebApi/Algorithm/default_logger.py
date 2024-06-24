import logging

logger = logging.getLogger('log')
logger.setLevel(logging.INFO)

stream = logging.StreamHandler()
stream.setLevel(logging.INFO)

logger.addHandler(stream)