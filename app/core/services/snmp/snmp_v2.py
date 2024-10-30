from typing import List, Optional, Tuple, Any, Dict

import asyncio

from core.services.snmp.snmp_base import SnmpBase, SnmpResultFormatter

from pysnmp.hlapi.asyncio import *

from core.config import settings


class SnmpV2(SnmpBase):
    """
    SNMPv2 walk по заданным IP-адресам коммутаторов.

    Attributes:
        target_ips (List[str]): Список IP-адресов для обхода.
        start_oid (str): Начальный OID для обхода.
        excluded_ports (Optional[List[int]]): Список портов для исключения.(default=None)
    """

    def __init__(
        self,
        target_ips: List[str],
        start_oid: str,
        excluded_ports: Optional[List[int]] = None,
    ):
        self.__snmp_engine = SnmpEngine()
        self.target_ips = target_ips
        self.start_oid = start_oid
        self.__context = ContextData()
        self.excluded_ports = excluded_ports
        self.community = CommunityData(settings.snmp.community)

    async def get_snmp_response(self, target_ip: str, current_oid: str) -> Tuple:
        """
        Выполняет SNMP-запрос к указанному IP-адресу для получения значения
        по заданному OID (Object Identifier).

        Эта функция создаёт корутину, которая выполняет SNMP-запрос и возвращает
        результат в виде кортежа, содержащего информацию о запросе.

        Args:
            target_ip (str): IP-адрес целевого SNMP-агента
            current_oid (str): OID, значение которого необходимо получить

        Returns:
            Tuple[ErrorIndication, Any, Any, Tuple[ObjectType, ...]]:
                Кортеж, содержащий информацию о запросе:
                - ErrorIndication: Указывает на наличие ошибок при выполнении запроса.
                - Any: Ответ от SNMP-агента.
                - Any: Дополнительная информация, связанная с ответом.
                - Tuple[ObjectType, ...]: Кортеж объектов типа ObjectType, представляющих запрашиваемые OID.
        """
        snmp_response_coroutine = next_cmd(
            self.__snmp_engine,
            self.community,
            await UdpTransportTarget.create((target_ip, 161)),
            self.__context,
            ObjectType(ObjectIdentity(current_oid)),
            lexicographicMode=True,
        )

        return await snmp_response_coroutine

    async def walk_all(self, method_name):
        """
        Создает список задач(корутин) вызывая method(ip) для каждого IP-адреса в self.target_ips.
        Метод asyncio.gather запускает все корутины из списка tasks параллельно и ожидает их завершения.


        Args:
            method_name: Метод для вызова

        Returns:
        """
        method = getattr(self, method_name)
        tasks = [method(ip) for ip in self.target_ips]
        results = await asyncio.gather(*tasks)

        combined_results = []
        for result in results:
            combined_results.extend(result)

        return combined_results


    async def walk_switch_ports(self, target_ip) -> List[Dict[str, Any]]:
        """
        Возвращает результат обхода по ветке OID,
        в случае перехода на другую ветвь цикл прерывается.
        :param target_ip:
        :return: List[Dict[str, Any]]
        Return example:
            [
                {
                    'SWITCH': '192.168.1.1':
                    'VLAN': 1721,
                    'MAC': "00:00:00:00:00:00",
                    'PORT': 1,
                },
                ...
            ]
        """
        current_oid = self.start_oid
        result = []

        while current_oid.startswith(self.start_oid):
            snmp_response = self.get_snmp_response(target_ip=target_ip, current_oid=current_oid)

            formatted_response = SwitchFormatter(*await snmp_response, self.start_oid)

            if formatted_response.get_error_message():
                result.extend([{"SWITCH": formatted_response.get_error_message()}])
                break
            else:
                formatted_result, current_oid = formatted_response.get_vlan_mac_port(
                    target_ip=target_ip, excluded_ports=self.excluded_ports
                )

                if formatted_result:
                    result.append(formatted_result)
                continue
        print(result)
        return result


class SwitchFormatter(SnmpResultFormatter):

    def __init__(self, errorIndication: Any, errorStatus: Any, errorIndex: Any, varBinds: List[Tuple], start_oid: str):
        super().__init__(errorIndication, errorStatus, errorIndex, varBinds, start_oid)

    def get_vlan_mac_port(self, target_ip, excluded_ports: Optional[List[int]]) -> Tuple[Dict, str]:
        current_oid = None
        formatted_result = None

        if not self.var_binds:
            raise ValueError(f"OIDs not found, varBinds: {self.var_binds}")

        for var_bind in self.var_binds:
            port = var_bind[1].prettyPrint() if var_bind else None
            current_oid = str(var_bind[0])

            if not current_oid.startswith(self.start_oid):
                break

            if int(port) in excluded_ports:
                break

            dis_branched_oid = self.dis_branch_oid(current_oid)
            decimal_mac1 = map(int, dis_branched_oid[1:])

            vlan = dis_branched_oid[0]
            mac = ":".join(f"{num:02x}" for num in decimal_mac1).upper()

            var_bind_data = {
                "SWITCH": target_ip,
                "VLAN": vlan,
                "MAC": mac,
                "PORT": port,
            }
            formatted_result = var_bind_data
        return formatted_result, current_oid
