from collections import defaultdict
from typing import Dict, List


class SnmpResponseMerger:

    def __init__(self, core_switch_data: Dict, switch_data: List):
        self.core_switch_data = core_switch_data
        self.switch_data = switch_data

    def merge_switches(self):
        """
        КОСТЫЛЬ переделать
        Returns:

        """
        core_switch_ip = next(iter(self.core_switch_data.keys()))

        for switch_device in self.switch_data:
            for core_switch, core_devices in self.core_switch_data.items():
                for device in core_devices:
                    if switch_device["MAC"] == device["MAC"]:
                        switch_device["IP"] = device["IP"]
                    else:
                        continue

        grouped_data = defaultdict(list)

        for entry in self.switch_data:
            grouped_data[entry["SWITCH"]].append(
                {"VLAN": entry["VLAN"], "MAC": entry["MAC"], "PORT": entry["PORT"], "IP": entry["IP"]}
            )

        merged_result = [{"SWITCH": switch, "devices": entries} for switch, entries in grouped_data.items()]

        return merged_result, core_switch_ip
