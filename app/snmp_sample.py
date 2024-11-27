from core.models import db_helper
from core.services.crud.crud_core_sw import CrudCoreSwitch
from core.services.crud.crud_device import CrudDevice
from core.services.snmp import SnmpResponseMerger, SnmpV2, SnmpV3
from core.services.snmp.snmp_formatters import CoreSwitchFormatter, SwitchFormatter
from schemas.device import DevicesSnmpResponse


async def add_snmp_to_data_base() -> bool:

    async with db_helper.session_factory() as session:

        crud_core_switch = CrudCoreSwitch(session=session)
        devices = CrudDevice(session=session)

        core_sw_params = await crud_core_switch.get_snmp_params()

        for core in core_sw_params:
            target_core_switch = [{"target_ip": core["core_switch_ip"], "snmp_oid": core["oid"]}]

            target_switches = [*core["switches"]]

            switch_walker = SnmpV2(SwitchFormatter)
            switch_snmp_response = await switch_walker.walk_all("get_mac_vlan_port_mappings", target_switches)

            core_walker = SnmpV3(CoreSwitchFormatter)
            core_sw_snmp_response = await core_walker.walk_all("get_arp_table", target_core_switch)

            merger = SnmpResponseMerger(switch_data=switch_snmp_response, core_switch_data=core_sw_snmp_response)
            merged_result, core_switch_ip = merger.merge_switches()

            device_data_list = DevicesSnmpResponse(switches=merged_result)

            await devices.create(device_data_list)

        return True
