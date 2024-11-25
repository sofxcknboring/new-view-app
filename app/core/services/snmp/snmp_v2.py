from typing import List, Tuple, Dict, Any, Optional

import asyncio

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
    async def get_sys_descr(self, target_ip, current_oid="1.3.6.1.2.1.1.1"):
        snmp_response = self.get_snmp_response(ip_address=target_ip, snmp_oid=current_oid)
        formatter = self.format_class(*await snmp_response, start_oid=current_oid)
        formatted_response = formatter.format_sys_descr()
        return formatted_response

    @snmp_logger
    async def get_port_vlan_table(self, ip_address: str, snmp_oid="1.3.6.1.2.1.17.7.1.4.5.1.1"):
        current_oid = snmp_oid
        result = []

        while current_oid.startswith(snmp_oid):
            snmp_response = self.get_snmp_response(ip_address=ip_address, snmp_oid=current_oid)
            formatter = self.format_class(*await snmp_response, start_oid=snmp_oid)

            port, current_oid = formatter.format_port_vlan_table()
            if port:
                result.append(port)
            else:
                continue
        return result

    @snmp_logger
    async def get_mac_vlan_port_mappings(
            self,
            target_ip,
            ports,
            snmp_oid='1.3.6.1.2.1.17.7.1.2.2.1.2'
    ) -> List[Dict[str, Any]]:

        current_oid = snmp_oid
        result = []

        while current_oid.startswith(snmp_oid):
            snmp_response = self.get_snmp_response(ip_address=target_ip, snmp_oid=current_oid)

            formatter = self.format_class(*await snmp_response, start_oid=snmp_oid)

            formatted_result, current_oid = formatter.format_vlan_mac_port_mapping(
                ip_address=target_ip, ports=ports
            )
            if formatted_result:
                result.append(formatted_result)
            continue
        return result

    async def get_arp_table(self, ip_address: str, snmp_oid: str):
        pass

    async def walk_all(self, method_name: str, target_switches) -> List:
        method = getattr(self, method_name)
        tasks = [method(**switch) for switch in target_switches]
        results = await asyncio.gather(*tasks)

        combined_results = []
        for result in results:
            combined_results.extend(result)

        return combined_results
