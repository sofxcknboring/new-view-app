import json

from core.models import db_helper
from core.services.crud.crud_core_sw import CrudCoreSwitch
from core.services.crud.crud_device import CrudDevice
from core.services.crud.crud_switch import CrudSwitch
from core.services.snmp import SnmpResponseMerger, SnmpV2, SnmpV3
from schemas.device import DeviceCreate, DeviceDataList


async def add_snmp_to_data_base() -> bool:

    async with db_helper.session_factory() as session:
        # Create Session
        crud_switch = CrudSwitch(session=session)
        crud_core_switch = CrudCoreSwitch(session=session)

        # get params
        switches_params = await crud_switch.get_snmp_params()
        core_sw_params = await crud_core_switch.get_snmp_params()

        switch_snmp_response = None
        core_sw_snmp_response = None

        # create snmp walkers and walk all

        if isinstance(switches_params, list) and all(isinstance(switch, dict) for switch in switches_params):

            switch_walker = SnmpV2(target_switches=switches_params)
            switch_snmp_response = await switch_walker.walk_all("get_switch_ports")

        if isinstance(core_sw_params, list) and all(isinstance(core, dict) for core in core_sw_params):

            core_walker = SnmpV3(target_switches=core_sw_params)
            core_sw_snmp_response = await core_walker.walk_all("get_arp_table")

        # merge snmp responses
        merger = SnmpResponseMerger(switch_data=switch_snmp_response, core_switch_data=core_sw_snmp_response)
        merged_result, core_switch_ip = merger.merge_switches()

        with open("./snmp_result.json", "w") as file:
            json.dump(merged_result, file, ensure_ascii=False, indent=4)

        # add to data_base

        devices = CrudDevice(session=session)

        device_data_list = DeviceDataList(devices=[DeviceCreate(**device) for device in merged_result])

        await devices.create(device_data_list)

        return True
