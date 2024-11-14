import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple

from core.config import settings
from core.services.snmp.snmp_base import SnmpBase
from core.services.snmp.snmp_formatters import SwitchFormatter
from pysnmp.hlapi.asyncio import *


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt="'%Y-%m-%d %H:%M:%S'"
)
logger = logging.getLogger(__name__)


class SnmpV2(SnmpBase):
    """
    SNMPv2 walk по заданным IP-адресам коммутаторов.

    Класс реализует функциональность обхода SNMPv2 для получения информации
    о коммутаторах по заданным IP-адресам. Он позволяет выполнять SNMP-запросы
    и обрабатывать ответы от SNMP-агента.

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
        logger.info("Run SNMPv2 -> switch IP: %s (OID: %s)", ip_address, snmp_oid)
        current_oid = snmp_oid
        result = []

        while current_oid.startswith(snmp_oid):
            try:
                snmp_response = self.get_snmp_response(ip_address=ip_address, snmp_oid=current_oid)

                formatted_response = SwitchFormatter(*await snmp_response, start_oid=snmp_oid)

                formatted_result, current_oid = formatted_response.get_vlan_mac_port(
                    ip_address=ip_address, excluded_ports=excluded_ports
                )
                if formatted_result:
                    result.append(formatted_result)
                continue
            except Exception as e:
                logger.error("SnmpV2(method: get_switch_ports() -> IP: (%s) - Error: %s", ip_address, e)
                break
        logger.info("Completed for IP: %s", ip_address)
        return result
