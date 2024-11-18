import asyncio

from core.models import db_helper
from core.services.crud.crud_core_sw import CrudCoreSwitch
from core.services.crud.crud_device import CrudDevice
from core.services.snmp import SnmpResponseMerger, SnmpV2, SnmpV3
from schemas.device import DevicesSnmpResponse


async def add_snmp_to_data_base() -> bool:

    async with db_helper.session_factory() as session:
        # Create Session
        crud_core_switch = CrudCoreSwitch(session=session)
        devices = CrudDevice(session=session)

        core_sw_params = await crud_core_switch.get_snmp_params()

        for core in core_sw_params:
            target_core_switch = [{"ip_address": core["core_switch_ip"], "snmp_oid": core["oid"]}]

            target_switches = [*core["switches"]]

            switch_walker = SnmpV2(target_switches=target_switches)
            switch_snmp_response = await switch_walker.walk_all("get_switch_ports")

            core_walker = SnmpV3(target_switches=target_core_switch)
            core_sw_snmp_response = await core_walker.walk_all("get_arp_table")

            merger = SnmpResponseMerger(switch_data=switch_snmp_response, core_switch_data=core_sw_snmp_response)
            merged_result, core_switch_ip = merger.merge_switches()

            device_data_list = DevicesSnmpResponse(switches=merged_result)

            await devices.create(device_data_list)

        return True





async def get_tr_prts():

    switch = [{
            # "ip_address": '10.254.244.6',
            # "snmp_oid": "1.3.6.1.2.1.17.7.1.4.5.1.1",
            # "excluded_ports": []
    }]

    switch_walker = SnmpV2(target_switches=switch)
    await switch_walker.get_info('10.254.243.5', "1.3.6.1.2.1.17.7.1.4.5.1.1")

#asyncio.run(get_tr_prts())