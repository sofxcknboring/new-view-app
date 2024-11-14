import asyncio

from core.models import db_helper
from core.services.crud.crud_core_sw import CrudCoreSwitch
from core.services.crud.crud_device import CrudDevice
from core.services.snmp import SnmpResponseMerger, SnmpV2, SnmpV3
from schemas.device import DevicesSnmpResponse


async def add_snmp_db():

    async with db_helper.session_factory() as session:
        # Create Session
        crud_core_switch = CrudCoreSwitch(session=session)
        devices = CrudDevice(session=session)

        core_sw_params = await crud_core_switch.get_snmp_params()

        for core in core_sw_params:
            target_core_switch = [{"ip_address": core["core_switch_ip"], "snmp_oid": core["oid"]}]

            target_switches = [*core["switches"]]
            print(target_core_switch)
            print(type(target_core_switch))
            print(target_switches)
            print(type(target_switches))

            switch_walker = SnmpV2(target_switches=target_switches)
            switch_snmp_response = await switch_walker.walk_all("get_switch_ports")

            core_walker = SnmpV3(target_switches=target_core_switch)
            core_sw_snmp_response = await core_walker.walk_all("get_arp_table")

            merger = SnmpResponseMerger(switch_data=switch_snmp_response, core_switch_data=core_sw_snmp_response)
            merged_result, core_switch_ip = merger.merge_switches()

            device_data_list = DevicesSnmpResponse(switches=merged_result)

            await devices.create(device_data_list)
            print(f"{core_switch_ip} added")


asyncio.run(add_snmp_db())
