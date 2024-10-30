from typing import Dict, List


class SnmpResponseMerger:

    def __init__(self, core_switch_data: Dict, switch_data: List):
        self.core_switch_data = core_switch_data
        self.switch_data = switch_data

    def merge_switches(self):

        core_switch_ip = next(iter(self.core_switch_data.keys()))

        for switch_device in self.switch_data:
            for core_switch, core_devices in self.core_switch_data.items():
                for device in core_devices:
                    if switch_device["MAC"] == device["MAC"]:
                        switch_device["IP"] = device["IP"]
                    else:
                        continue

        return self.switch_data, core_switch_ip
