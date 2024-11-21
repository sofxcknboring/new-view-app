from abc import ABC, abstractmethod
from typing import Any, List, Tuple

from pysnmp.error import PySnmpError


class SnmpResultFormatter(ABC):
    def __init__(
            self, error_indication: Any, error_status: Any, error_index: Any, var_binds: List[Tuple], start_oid: str
    ):
        self.error_indication = error_indication
        self.error_status = error_status
        self.error_index = error_index
        self.var_binds = var_binds
        self.start_oid = start_oid

    def find_exceptions(self) -> bool:
        if self.error_indication:
            raise PySnmpError(f"SNMP Error Indication: {self.error_indication}")

        if self.error_status:
            raise PySnmpError(f"SNMP Error Status: {self.error_status.prettyPrint()} at index {self.error_index}")

        if not self.var_binds:
            raise ValueError(f"OIDs not found, varBinds: {self.var_binds}")

        return True

    @abstractmethod
    def format_info(self):
        pass

    def dis_branch_oid(self, oid: str):
        return oid.replace(f"{self.start_oid}.", "").split(".")