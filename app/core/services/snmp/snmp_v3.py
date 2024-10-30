from typing import List, Tuple, Any, Dict

import asyncio
import re

from core.services.snmp.snmp_base import SnmpBase, SnmpResultFormatter

from pysnmp.hlapi.asyncio import *

from core.config import settings

class SnmpV3(SnmpBase):
    """
    SNMPv2 walk по заданным IP-адресам.

    Attributes:
        target_ips (List[str]): Список IP-адресов для обхода.
        start_oid (str): Начальный OID для обхода.
    """

    def __init__(
        self,
        target_ips: List[str],
        start_oid: str,
        user: str = settings.snmp.username,
        auth_proto: str = settings.snmp.auth_key,
        priv_proto: str = settings.snmp.priv_key,
    ):
        self.__snmp_engine = SnmpEngine()
        self.target_ips = target_ips
        self.start_oid = start_oid
        self.__context = ContextData()
        self.user = UsmUserData(
            user, auth_proto, priv_proto, authProtocol=usmHMACSHAAuthProtocol, privProtocol=usmAesCfb128Protocol
        )

    async def get_snmp_response(self, target_ip, current_oid):
        """
        Выполняет SNMP-запрос к указанному IP-адресу для получения значения
        по заданному OID (Object Identifier).

        Эта функция создаёт корутину, которая выполняет SNMP-запрос и возвращает
        результат в виде кортежа, содержащего информацию о запросе.

        Args:
            target_ip (str): IP-адрес целевого SNMP-агента.
            current_oid (str): OID, значение которого необходимо получить.

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
            await UdpTransportTarget.create((target_ip, 161)),
            self.__context,
            ObjectType(ObjectIdentity(current_oid)),
            lexicographicMode=True,
        )

        return await snmp_response_coroutine

    async def walk_all(self, method_name) -> Dict[str, List]:
        """
        Создает список задач(корутин) вызывая method(ip) для каждого IP-адреса в self.target_ips.
        Метод asyncio.gather запускает все корутины из списка tasks параллельно и ожидает их завершения.


        Args:
            method_name: Метод для вызова

        Returns: List[Dict[str, List[Dict[str, Any]]]]
        """
        method = getattr(self, method_name)
        tasks = [method(ip) for ip in self.target_ips]
        results = await asyncio.gather(*tasks)

        combined_results = {}
        for result in results:
            for ip, data in result.items():
                if ip not in combined_results:
                    combined_results[ip] = []
                combined_results[ip].extend(data)

        return combined_results

    async def walk_arp_table(self, target_ip):
        current_oid = self.start_oid
        result = {target_ip: []}

        while current_oid.startswith(self.start_oid):
            snmp_response = self.get_snmp_response(target_ip=target_ip, current_oid=current_oid)

            formatted_response = CoreSwitchFormatter(*await snmp_response, self.start_oid)

            if formatted_response.get_error_message():
                result[target_ip].extend({f"{target_ip}": formatted_response.get_error_message()})
                break
            else:
                formatted_result, current_oid = formatted_response.get_vlan_mac_ip(
                    target_ip=target_ip
                )

                result[target_ip].extend(formatted_result[target_ip])

        return result


class CoreSwitchFormatter(SnmpResultFormatter):

    def __init__(self, errorIndication: Any, errorStatus: Any, errorIndex: Any, varBinds: List[Tuple], start_oid: str):
        super().__init__(errorIndication, errorStatus, errorIndex, varBinds, start_oid)

    def get_vlan_mac_ip(self, target_ip) -> Tuple[Dict, str]:
        current_oid = None
        formatted_result = {target_ip: []}

        if not self.var_binds:
            raise ValueError(f"OIDs not found, varBinds: {self.var_binds}")

        for var_bind in self.var_binds:
            mac = var_bind[1].prettyPrint() if var_bind else None
            current_oid = str(var_bind[0])

            if not current_oid.startswith(self.start_oid):
                break

            dis_branched_oid = self.dis_branch_oid(current_oid)

            vlan = dis_branched_oid[0]

            f_mac = re.findall(".{2}", mac)
            mac = ":".join(f_mac[1:]).upper()
            ip = ".".join(dis_branched_oid[1:])

            var_bind_data = {
                "VLAN": vlan,
                "MAC": mac,
                "IP": ip,
            }
            formatted_result[target_ip].append(var_bind_data)
        return formatted_result, current_oid

