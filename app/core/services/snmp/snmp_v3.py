import asyncio
import logging
from typing import Any, Dict, List, Tuple

from core.config import settings
from core.services.snmp.formatter_base import SnmpResultFormatter
from core.services.snmp.snmp_base import SnmpBase
from core.services.snmp.snmp_logger import snmp_logger
from pysnmp.hlapi.asyncio import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SnmpV3(SnmpBase):
    """
    SNMPv3 walk по заданным IP-адресам.
    """

    def __init__(
        self,
        format_class: type[SnmpResultFormatter],
        user: str = settings.snmp.username,
        auth_proto: str = settings.snmp.auth_key,
        priv_proto: str = settings.snmp.priv_key,
    ):
        super().__init__(format_class)
        self.user = UsmUserData(
            user, auth_proto, priv_proto, authProtocol=usmHMACSHAAuthProtocol, privProtocol=usmAesCfb128Protocol
        )

    async def get_snmp_response(self, ip_address, snmp_oid) -> Tuple:

        snmp_response_coroutine = next_cmd(
            self.snmp_engine,
            self.user,
            await UdpTransportTarget.create((ip_address, 161)),
            self.context,
            ObjectType(ObjectIdentity(snmp_oid)),
            lexicographicMode=True,
        )

        return await snmp_response_coroutine

    @snmp_logger
    async def get_sys_descr(self, target_ip, current_oid="1.3.6.1.2.1.1.1"):
        snmp_response = self.get_snmp_response(ip_address=target_ip, snmp_oid=current_oid)
        formatter = self.format_class(*await snmp_response, start_oid=current_oid)
        formatted_response = formatter.format_sys_descr()
        return formatted_response

    async def get_port_vlan_table(self, target_ip, current_oid):
        pass

    @snmp_logger
    async def get_arp_table(self, target_ip: str, snmp_oid="1.3.6.1.2.1.4.22.1.2") -> Dict[Any, Any]:

        current_oid = snmp_oid
        result = {target_ip: []}

        while current_oid.startswith(snmp_oid):
            try:
                snmp_response = self.get_snmp_response(ip_address=target_ip, snmp_oid=current_oid)
                formatter = self.format_class(*await snmp_response, start_oid=snmp_oid)
                formatted_result, current_oid = formatter.format_arp_table(ip_address=target_ip)
                result[target_ip].extend(formatted_result[target_ip])
            except Exception:
                raise
        return result

    async def get_mac_vlan_port_mappings(self, target_ip, ports, snmp_oid):
        pass

    async def walk_all(self, method_name, target_switches) -> Dict[str, List]:
        method = getattr(self, method_name)
        tasks = [method(**switch) for switch in target_switches]
        results = await asyncio.gather(*tasks)

        combined_results = {}
        for result in results:
            for ip, data in result.items():
                if ip not in combined_results:
                    combined_results[ip] = []
                combined_results[ip].extend(data)

        return combined_results
