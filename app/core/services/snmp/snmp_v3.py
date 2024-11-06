import asyncio
from typing import Any, Dict, List, Tuple

from core.config import settings
from core.services.snmp.snmp_base import SnmpBase
from core.services.snmp.snmp_formatters import CoreSwitchFormatter
from pysnmp.hlapi.asyncio import *


class SnmpV3(SnmpBase):
    """
    SNMPv3 walk по заданным IP-адресам.

    Attributes:
        target_switches: List[Dict[str, str]

    Examples:
        {
            "ip_address": "IP-адрес коммутатора". - '192.168.1.1'
            "snmp_oid": "OID для обхода" - '1.3.6.1.....'
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
        """
        Выполняет SNMP-запрос к указанному IP-адресу для получения значения
        по заданному OID (Object Identifier).

        Эта функция создаёт корутину, которая выполняет SNMP-запрос и возвращает
        результат в виде кортежа, содержащего информацию о запросе.

        Args:
            ip_address (str): IP-адрес целевого SNMP-агента.
            snmp_oid (str): OID, значение которого необходимо получить.

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
            self.user,
            await UdpTransportTarget.create((ip_address, 161)),
            self.__context,
            ObjectType(ObjectIdentity(snmp_oid)),
            lexicographicMode=True,
        )

        return await snmp_response_coroutine

    async def walk_all(self, method_name) -> Dict[str, List]:
        """
        Создает список задач(корутин) вызывая method(ip) для каждого IP-адреса в self.target_ips.
        Метод asyncio.gather запускает все корутины из списка tasks параллельно и ожидает их завершения.


        Args:
            method_name: Метод для вызова -> .walk_all("get_arp_table")

        Returns: Dict[str, List]
        """
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
        current_oid = snmp_oid
        result = {ip_address: []}

        while current_oid.startswith(snmp_oid):
            snmp_response = self.get_snmp_response(ip_address=ip_address, snmp_oid=current_oid)

            formatted_response = CoreSwitchFormatter(*await snmp_response, start_oid=snmp_oid)

            formatted_result, current_oid = formatted_response.get_vlan_mac_ip(ip_address=ip_address)

            result[ip_address].extend(formatted_result[ip_address])

        return result
