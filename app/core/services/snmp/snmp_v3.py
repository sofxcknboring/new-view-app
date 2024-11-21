import asyncio
import logging
from typing import Any, Dict, List, Tuple

from core.config import settings
from core.services.snmp.snmp_base import SnmpBase
from core.services.snmp.snmp_formatters import CoreSwitchFormatter
from pysnmp.hlapi.asyncio import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SnmpV3(SnmpBase):
    """
    SNMPv3 walk по заданным IP-адресам.
    """

    def __init__(
        self,
        target_switches: List[Dict[str, str]],
        user: str = settings.snmp.username,
        auth_proto: str = settings.snmp.auth_key,
        priv_proto: str = settings.snmp.priv_key,
    ):
        self.__snmp_engine = SnmpEngine()
        self.target_switches = target_switches
        self.__context = ContextData()
        self.user = UsmUserData(
            user, auth_proto, priv_proto, authProtocol=usmHMACSHAAuthProtocol, privProtocol=usmAesCfb128Protocol
        )

    async def get_snmp_response(self, ip_address, snmp_oid) -> Tuple:

        snmp_response_coroutine = next_cmd(
            self.__snmp_engine,
            self.user,
            await UdpTransportTarget.create((ip_address, 161)),
            self.__context,
            ObjectType(ObjectIdentity(snmp_oid)),
            lexicographicMode=True,
        )

        return await snmp_response_coroutine

    async def walk_all(self, method_name) -> Dict[str, List]:

        method = getattr(self, method_name)
        tasks = [method(**switch) for switch in self.target_switches]
        results = await asyncio.gather(*tasks)

        combined_results = {}
        for result in results:
            for ip, data in result.items():
                if ip not in combined_results:
                    combined_results[ip] = []
                combined_results[ip].extend(data)

        return combined_results

    async def get_arp_table(self, ip_address: str, snmp_oid: str) -> Dict[Any, Any]:

        logger.info("Run SNMPv3 -> Core switch IP: %s (OID: %s)", ip_address, snmp_oid)

        current_oid = snmp_oid
        result = {ip_address: []}

        while current_oid.startswith(snmp_oid):
            try:
                snmp_response = self.get_snmp_response(ip_address=ip_address, snmp_oid=current_oid)

                formatted_response = CoreSwitchFormatter(*await snmp_response, start_oid=snmp_oid)

                formatted_result, current_oid = formatted_response.get_vlan_mac_ip(ip_address=ip_address)

                result[ip_address].extend(formatted_result[ip_address])
            except Exception as e:
                logger.error("SnmpV3(method: get_arp_table() -> IP: (%s) - Error: %s", ip_address, e)
                break

        logger.info("SnmpV3(method: get_arp_table() -> Completed for IP: %s", ip_address)
        return result
