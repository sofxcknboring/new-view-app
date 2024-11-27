import re
from typing import Any, Dict, List, Optional, Tuple

from core.services.snmp.snmp_base import SnmpResultFormatter
from schemas.validation_helper import validation_helper


class SwitchFormatter(SnmpResultFormatter):

    def __init__(self, errorIndication: Any, errorStatus: Any, errorIndex: Any, varBinds: List[Tuple], start_oid: str):
        super().__init__(errorIndication, errorStatus, errorIndex, varBinds, start_oid)

    def format_sys_descr(self):
        self.find_exceptions()

        for var_bind in self.var_binds:
            value = var_bind[1]
            bytes_value = value.asOctets()
            decoded_value = bytes_value.decode("utf-8", errors="ignore")
            device_name = decoded_value.split(",")[:1]
            return ",".join(device_name)

    def format_port_vlan_table(self) -> Tuple[Optional[int], str]:
        """
        Returns:
            (port(int | None), current_oid: str)
        """
        current_oid = None
        self.find_exceptions()

        for var_bind in self.var_binds:
            vlan = int(var_bind[1].prettyPrint()) if var_bind else None

            current_oid = str(var_bind[0])

            if not current_oid.startswith(self.start_oid):
                break
            if vlan != 1:
                return int(var_bind[0][-1]), current_oid
            else:
                return None, current_oid
        return None, current_oid

    def format_vlan_mac_port_mapping(self, ip_address, ports: Optional[List[int]]) -> Tuple[Dict, str]:
        current_oid = None
        formatted_result = None

        self.find_exceptions()

        for var_bind in self.var_binds:
            port = validation_helper.validate_port(var_bind[1].prettyPrint() if var_bind else None)

            current_oid = str(var_bind[0])

            if not current_oid.startswith(self.start_oid):
                break

            if port not in ports:
                break

            dis_branched_oid = self.dis_branch_oid(current_oid)
            decimal_mac1 = map(int, dis_branched_oid[1:])

            vlan = dis_branched_oid[0]
            mac = ":".join(f"{num:02x}" for num in decimal_mac1).upper()

            var_bind_data = {"SWITCH": ip_address, "VLAN": vlan, "MAC": mac, "PORT": port, "IP": "NOT_FOUND"}
            formatted_result = var_bind_data
        return formatted_result, current_oid

    async def format_arp_table(self, ip_address):
        pass


class CoreSwitchFormatter(SnmpResultFormatter):

    def __init__(self, errorIndication: Any, errorStatus: Any, errorIndex: Any, varBinds: List[Tuple], start_oid: str):
        super().__init__(errorIndication, errorStatus, errorIndex, varBinds, start_oid)

    def format_sys_descr(self):
        self.find_exceptions()

        for var_bind in self.var_binds:
            value = var_bind[1]
            bytes_value = value.asOctets()
            decoded_value = bytes_value.decode("utf-8", errors="ignore")
            device_name = decoded_value.split(",")[:3]
            return ",".join(device_name)

    def format_port_vlan_table(self):
        pass

    def format_vlan_mac_port_mapping(self, ip_address, ports):
        pass

    def format_arp_table(self, ip_address: str) -> Tuple[Dict, str]:
        current_oid = None
        formatted_result = {ip_address: []}

        self.find_exceptions()

        for var_bind in self.var_binds:
            mac = var_bind[1].prettyPrint()
            current_oid = str(var_bind[0])

            if not current_oid.startswith(self.start_oid):
                break

            dis_branched_oid = self.dis_branch_oid(current_oid)

            vlan = int(dis_branched_oid[0])
            f_mac = re.findall(".{2}", mac)
            mac = ":".join(f_mac[1:]).upper()
            ip = validation_helper.validate_ip_address(".".join(dis_branched_oid[1:]))

            var_bind_data = {
                "VLAN": vlan,
                "MAC": mac,
                "IP": ip,
            }

            formatted_result[ip_address].append(var_bind_data)

        return formatted_result, current_oid
