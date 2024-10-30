from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple


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
    def __init__(
        self, error_indication: Any, error_status: Any, error_index: Any, var_binds: List[Tuple], start_oid: str
    ):
        self.error_indication = error_indication
        self.error_status = error_status
        self.error_index = error_index
        self.var_binds = var_binds
        self.start_oid = start_oid

    def has_error(self) -> bool:
        return self.error_indication is not None or self.error_status is not None

    def get_error_message(self) -> Optional[str]:
        if self.error_indication:
            return str(self.error_indication)
        elif self.error_status:
            return f"{self.error_status.prettyPrint()} at index {self.error_index}"
        return None

    def dis_branch_oid(self, oid: str):
        """
        Исключает ветку из строки OID и возвращает оставшуюся часть в виде списка.

        :return: List[str]: Список строк, представляющих оставшуюся часть OID.
        Example:
            oid = '1.3.6.1.2.1.17.7.1.2.2.1.2.1721.192.168.1.1'
            return ['1721', '192.168.1.1']
        """
        return oid.replace(f"{self.start_oid}.", "").split(".")
