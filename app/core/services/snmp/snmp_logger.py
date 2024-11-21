import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt="'%Y-%m-%d %H:%M:%S'"
)
logger = logging.getLogger(__name__)


def snmp_logger(func):
    async def wrapper(*args, **kwargs):
        logger.info(f"SNMPv2({func.__name__}) -> IP: %s (OID: %s)", *args)
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"SnmpV2({func.__name__}) -> IP: %s - Error: %s", *args, e)

    return wrapper
