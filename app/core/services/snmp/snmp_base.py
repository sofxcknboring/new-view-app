from abc import ABC, abstractmethod
from pysnmp.hlapi.asyncio import *

from core.services.snmp.formatter_base import SnmpResultFormatter


class SnmpBase(ABC):
    def __init__(self, format_class: type[SnmpResultFormatter]):
        self.snmp_engine = SnmpEngine()
        self.context = ContextData()
        self.format_class = format_class

    @abstractmethod
    async def get_snmp_response(self, target_ip, current_oid):
        pass

    @abstractmethod
    async def walk_all(self, method_name):
        pass
