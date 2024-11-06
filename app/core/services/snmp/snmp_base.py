from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple
from pysnmp.error import PySnmpError


class SnmpBase(ABC):

    @abstractmethod
    async def get_snmp_response(self, target_ip, current_oid):
        """
        Args:
            target_ip (str): IP-адрес целевого SNMP-агента
            current_oid (str): OID, значение которого необходимо получить

        Returns:
            Картеж с ответом от SNMP-агента.
        """
        pass

    @abstractmethod
    async def walk_all(self, method_name):
        pass


class SnmpResultFormatter(ABC):
    """
    Абстрактный класс для форматирования результатов SNMP-запросов.

    Этот класс предоставляет базовую функциональность для обработки результатов SNMP-запросов,
    включая управление ошибками и извлечение OID. Конкретные реализации этого класса должны
    предоставлять методы для форматирования и представления данных в удобном виде.

    Attributes:
        error_indication (Any): Указывает на наличие ошибки в результате запроса.
        error_status (Any): Статус ошибки, если таковой имеется.
        error_index (Any): Индекс, связанный с ошибкой, если таковой имеется.
        var_binds (List[Tuple]): Список переменных, полученных в результате запроса.
        start_oid (str): Начальный OID, используемый для обработки и форматирования OID.

    Methods:

        dis_branch_oid(oid: str) -> List[str]:
            Исключает ветку из строки OID и возвращает оставшуюся часть в виде списка.

    """

    def __init__(
        self, error_indication: Any, error_status: Any, error_index: Any, var_binds: List[Tuple], start_oid: str
    ):
        self.error_indication = error_indication
        self.error_status = error_status
        self.error_index = error_index
        self.var_binds = var_binds
        self.start_oid = start_oid

    def find_exceptions(self) -> bool:
        """
        Raises:
            PySnmpError(SNMP Error Indication) -> self.error_indication
            PySnmpError(SNMP Error Status) -> self.error_status
            ValueError(OIDs not found, varBinds) -> Если переменные OID не найдены (varBinds пуст).
        """
        if self.error_indication:
            raise PySnmpError(f"SNMP Error Indication: {self.error_indication}")

        if self.error_status:
            raise PySnmpError(f"SNMP Error Status: {self.error_status.prettyPrint()} at index {self.error_index}")

        if not self.var_binds:
            raise ValueError(f"OIDs not found, varBinds: {self.var_binds}")

        return True

    def dis_branch_oid(self, oid: str):
        """
        Исключает ветку из строки OID и возвращает оставшуюся часть в виде списка.

        :return: List[str]: Список строк, представляющих оставшуюся часть OID.
        Example:
            oid = '1.3.6.1.2.1.17.7.1.2.2.1.2.1721.192.168.1.1'
            return ['1721', '192.168.1.1']
        """
        return oid.replace(f"{self.start_oid}.", "").split(".")
