import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def wait(seconds: int = 15) -> None:
    """
    Step 4: Wait for a specified number of seconds.
    
    Args:
        seconds (int): Number of seconds to wait
    """
    logger.info(f"Step 4: Waiting for {seconds} seconds...")
    for i in range(seconds, 0, -1):
        logger.info(f"Cleaning up in {i} seconds...")
        time.sleep(1)
    logger.info("Wait complete.")
