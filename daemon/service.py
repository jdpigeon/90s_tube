import logging
import time

logger = logging.getLogger(__name__)
logger.debug("Hello, world!")
logger.info("Hello, world!")
logger.error("Hello, world!")
print("Hello, world!")

while True:
    logger.debug("Hello, world!")
    logger.info("Hello, world!")
    logger.error("Hello, world!")
    print("Hello, world!")
    time.sleep(3)
