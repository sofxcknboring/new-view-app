from typing import List, Tuple
from .snmp_logger import snmp_logger
from core.config import settings
from core.services.snmp.snmp_base import SnmpBase
from pysnmp.hlapi.asyncio import *


class SnmpV2(SnmpBase):
    def __init__(self, format_class):
        super().__init__(format_class)
        self.community = CommunityData(settings.snmp.community)

    async def get_snmp_response(self, ip_address: str, snmp_oid: str) -> Tuple:

        snmp_response_coroutine = next_cmd(
            self.snmp_engine,
            self.community,
            await UdpTransportTarget.create((ip_address, 161)),
            self.context,
            ObjectType(ObjectIdentity(snmp_oid)),
            lexicographicMode=True,
        )

        return await snmp_response_coroutine

    @snmp_logger
    async def get_vlan_configuration(self, ip_address: str, snmp_oid="1.3.6.1.2.1.17.7.1.4.5.1.1"):
        current_oid = snmp_oid
        result = []

        while current_oid.startswith(snmp_oid):
            snmp_response = self.get_snmp_response(ip_address=ip_address, snmp_oid=current_oid)
            formatter = self.format_class(*await snmp_response, start_oid=snmp_oid)

            port, current_oid = formatter.format_info()
            if port:
                result.append(port)
            else:
                continue
        return result

    async def walk_all(self, method_name: str) -> List:
        pass
        # method = getattr(self, method_name)
        # tasks = [method(**switch) for switch in self.target_switches]
        # results = await asyncio.gather(*tasks)
        #
        # combined_results = []
        # for result in results:
        #     combined_results.extend(result)
        #
        # return combined_results

    # async def get_switch_ports(
    #     self, ip_address: str, snmp_oid: str, excluded_ports: Optional[List[int]]
    # ) -> List[Dict[str, Any]]:
    #     logger.info("Run SNMPv2 -> switch IP: %s (OID: %s)", ip_address, snmp_oid)
    #     current_oid = snmp_oid
    #     result = []
    #
    #     while current_oid.startswith(snmp_oid):
    #         try:
    #             snmp_response = self.get_snmp_response(ip_address=ip_address, snmp_oid=current_oid)
    #
    #             formatted_response = SwitchFormatter(*await snmp_response, start_oid=snmp_oid)
    #
    #             formatted_result, current_oid = formatted_response.get_vlan_mac_port(
    #                 ip_address=ip_address, excluded_ports=excluded_ports
    #             )
    #             if formatted_result:
    #                 result.append(formatted_result)
    #             continue
    #         except Exception as e:
    #             logger.error("SnmpV2(method: get_switch_ports() -> IP: (%s) - Error: %s", ip_address, e)
    #             break
    #     logger.info("Completed for IP: %s", ip_address)
    #     return result