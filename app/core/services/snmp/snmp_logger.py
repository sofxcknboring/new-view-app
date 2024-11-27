import logging
from functools import wraps

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="'%Y-%m-%d %H:%M:%S'"
)
logger = logging.getLogger(__name__)


def snmp_logger(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"start ({func.__name__})")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__}) Error: {str(e)}")
            raise

    return wrapper
