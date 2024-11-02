import asyncio
from typing import Any, Dict, List, Optional, Tuple

from core.config import settings
from core.services.snmp.snmp_base import SnmpBase, SnmpResultFormatter
from pysnmp.hlapi.asyncio import *


class SnmpV2(SnmpBase):
    """
    SNMPv2 walk по заданным IP-адресам коммутаторов.

    Класс реализует функциональность обхода SNMPv2 для получения информации
    о коммутаторах по заданным IP-адресам. Он позволяет выполнять SNMP-запросы
    и обрабатывать ответы, исключая определенные ответы от SNMP-агента.

    Attributes:
        target_switches: List[Dict[str, Any]

    Examples:
        {
            "ip_address": "IP-адрес коммутатора". - '192.168.1.1'
            "snmp_oid": "OID для обхода" - '1.3.6.1.....'
            "excluded_ports": [1, 2, 3, 4,...] Список портов для исключения.
        }
    """

    def __init__(
        self,
        target_switches: List[Dict[str, Any]],
    ):
        self.__snmp_engine = SnmpEngine()
        self.__context = ContextData()
        self.community = CommunityData(settings.snmp.community)
        self.target_switches = target_switches

    async def get_snmp_response(self, ip_address: str, snmp_oid: str) -> Tuple:
        """
        Выполняет SNMP-запрос к указанному IP-адресу для получения значения
        по заданному OID (Object Identifier).

        Эта функция создаёт корутину, которая выполняет SNMP-запрос и возвращает
        результат в виде кортежа, содержащего информацию о запросе.
        Результат ответа рекомендуется форматировать в удобную структуру через класс SnmpResultFormatter.
        Args:
            ip_address (str): IP-адрес целевого SNMP-агента
            snmp_oid (str): OID, значение которого необходимо получить

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
            await UdpTransportTarget.create((ip_address, 161)),
            self.__context,
            ObjectType(ObjectIdentity(snmp_oid)),
            lexicographicMode=True,
        )

        return await snmp_response_coroutine

    async def walk_all(self, method_name: str) -> List:
        """
        Создает список задач(корутин) вызывая method(**switch) для каждого IP-адреса в self.target_switches.
        Метод asyncio.gather запускает все корутины из списка tasks параллельно и ожидает их завершения.

        Args:
            method_name (str): Имя метода, который будет вызван для каждого IP-адреса.

        Returns:
            List: Объединенный список результатов, полученных от вызова метода для каждого IP-адреса.
        """
        method = getattr(self, method_name)
        tasks = [method(**switch) for switch in self.target_switches]
        results = await asyncio.gather(*tasks)

        combined_results = []
        for result in results:
            combined_results.extend(result)

        return combined_results

    async def get_switch_ports(
        self, ip_address: str, snmp_oid: str, excluded_ports: Optional[List[int]]
    ) -> List[Dict[str, Any]]:
        """
        Получает информацию о портах коммутатора для заданного IP-адреса, используя SNMP.

        Метод выполняет SNMP-запросы для извлечения информации о VLAN, MAC-адресах и портах,
        исключая указанные порты. Он продолжает запрашивать данные, пока текущий OID
        начинается с заданного начального OID.

        Args:
            ip_address (str): IP-адрес коммутатора, для которого извлекается информация
            snmp_oid (str): Начальный OID для SNMP-запросов, который будет использоваться для фильтрации
            excluded_ports (Optional[List[int]]): Список портов, которые следует исключить из результатов

        Returns:
            List[Dict[str, Any]]: Список словарей, содержащих информацию о портах коммутатора.
                                   Каждый словарь включает информацию о VLAN, MAC-адресе и порте.

        Raises:
            Exception: Может выбросить исключение, если возникла ошибка при получении SNMP-ответа.
        """
        current_oid = snmp_oid
        result = []

        while current_oid.startswith(snmp_oid):
            snmp_response = self.get_snmp_response(ip_address=ip_address, snmp_oid=current_oid)

            formatted_response = SwitchFormatter(*await snmp_response, start_oid=snmp_oid)

            if formatted_response.get_error_message():
                result.extend([{"SWITCH": formatted_response.get_error_message()}])
                break
            else:
                formatted_result, current_oid = formatted_response.get_vlan_mac_port(
                    ip_address=ip_address, excluded_ports=excluded_ports
                )
                if formatted_result:
                    result.append(formatted_result)
                continue
        return result


class SwitchFormatter(SnmpResultFormatter):

    def __init__(self, errorIndication: Any, errorStatus: Any, errorIndex: Any, varBinds: List[Tuple], start_oid: str):
        super().__init__(errorIndication, errorStatus, errorIndex, varBinds, start_oid)

    def get_vlan_mac_port(self, ip_address, excluded_ports: Optional[List[int]]) -> Tuple[Dict, str]:
        """
        Извлекает информацию о VLAN, MAC-адресах и портах для заданного IP-адреса.

        Args:
            ip_address (str): IP-адрес коммутатора, для которого извлекается информация.
            excluded_ports (Optional[List[int]]): Список портов, которые следует исключить из результатов.

        Returns:
            Tuple[Dict, str]: Кортеж, содержащий словарь с информацией о VLAN, MAC-адресе и порте,
                              а также текущий OID, если он был найден.

        Raises:
            ValueError: Если переменные OID не найдены (varBinds пуст).
        """
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
                "SWITCH": ip_address,
                "VLAN": vlan,
                "MAC": mac,
                "PORT": port,
            }
            formatted_result = var_bind_data
        return formatted_result, current_oid
