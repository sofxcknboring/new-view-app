from abc import ABC, abstractmethod

from core.services.snmp.formatter_base import SnmpResultFormatter
from pysnmp.hlapi.asyncio import *


class SnmpBase(ABC):
    def __init__(self, format_class: type[SnmpResultFormatter]):
        self.snmp_engine = SnmpEngine()
        self.context = ContextData()
        self.format_class = format_class

    @abstractmethod
    async def get_snmp_response(self, target_ip, current_oid):
        pass

    @abstractmethod
    async def get_sys_descr(self, target_ip, current_oid):
        pass

    @abstractmethod
    async def get_port_vlan_table(self, target_ip, current_oid):
        pass

    @abstractmethod
    async def get_mac_vlan_port_mappings(self, target_ip, ports, snmp_oid):
        pass

    @abstractmethod
    async def get_arp_table(self, target_ip, snmp_oid):
        pass

    @abstractmethod
    async def walk_all(self, method_name, target_switches):
        pass
