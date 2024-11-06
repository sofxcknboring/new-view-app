from core.services.snmp.snmp_base import SnmpResultFormatter
from typing import Any, List, Tuple, Dict, Optional
import re
from schemas.validation_helper import validation_helper


class SwitchFormatter(SnmpResultFormatter):

    def __init__(self, errorIndication: Any, errorStatus: Any, errorIndex: Any, varBinds: List[Tuple], start_oid: str):
        super().__init__(errorIndication, errorStatus, errorIndex, varBinds, start_oid)

    def get_vlan_mac_port(self, ip_address, excluded_ports: Optional[List[int]]) -> Tuple[Dict, str]:
        """
        Извлекает информацию о VLAN, MAC-адресах и портах для заданного IP-адреса коммутатора.

        Args:
            ip_address (str): IP-адрес коммутатора, для которого извлекается информация.
            excluded_ports (Optional[List[int]]): Список портов, которые следует исключить из результатов.

        Returns:
            Tuple[Dict, str]: Кортеж, содержащий словарь с информацией о VLAN, MAC-адресе и порте,
                              а также текущий OID, если он был найден.

        """
        current_oid = None
        formatted_result = None

        self.find_exceptions()

        for var_bind in self.var_binds:
            port = validation_helper.validate_port(var_bind[1].prettyPrint() if var_bind else None)
            current_oid = str(var_bind[0])

            if not current_oid.startswith(self.start_oid):
                break

            if port in excluded_ports:
                break

            dis_branched_oid = self.dis_branch_oid(current_oid)
            decimal_mac1 = map(int, dis_branched_oid[1:])

            vlan = dis_branched_oid[0]
            mac = ":".join(f"{num:02x}" for num in decimal_mac1).upper()

            var_bind_data = {"SWITCH": ip_address, "VLAN": vlan, "MAC": mac, "PORT": port, "IP": "NOT_FOUND"}
            formatted_result = var_bind_data
        return formatted_result, current_oid


class CoreSwitchFormatter(SnmpResultFormatter):

    def __init__(self, errorIndication: Any, errorStatus: Any, errorIndex: Any, varBinds: List[Tuple], start_oid: str):
        super().__init__(errorIndication, errorStatus, errorIndex, varBinds, start_oid)

    def get_vlan_mac_ip(self, ip_address: str) -> Tuple[Dict, str]:
        """
        Извлекает информацию о VLAN, MAC-адресах и IP для заданного IP-адреса коммутатора.

        Args:
            ip_address (str): IP-адрес опорного коммутатора, для которого извлекается информация.

        Returns:
            Tuple[Dict, str]: Кортеж, содержащий словарь с информацией о VLAN, MAC-адресе и IP,
                              а также текущий OID, если он был найден.
        """
        current_oid = None
        formatted_result = {ip_address: []}

        self.find_exceptions()

        for var_bind in self.var_binds:
            mac = var_bind[1].prettyPrint() if var_bind else None
            current_oid = str(var_bind[0])

            if not current_oid.startswith(self.start_oid):
                break

            dis_branched_oid = self.dis_branch_oid(current_oid)

            vlan = int(dis_branched_oid[0])
            f_mac = re.findall(".{2}", mac)
            mac = validation_helper.validate_mac_address(":".join(f_mac[1:]).upper())
            ip = validation_helper.validate_ip_address(".".join(dis_branched_oid[1:]))

            var_bind_data = {
                "VLAN": vlan,
                "MAC": mac,
                "IP": ip,
            }

            formatted_result[ip_address].append(var_bind_data)

        return formatted_result, current_oid
