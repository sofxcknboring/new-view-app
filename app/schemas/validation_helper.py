import re
from ipaddress import ip_address


class ValidationHelper:

    @staticmethod
    def validate_ip_address(ip: str) -> str:
        if not ip_address(ip):
            raise ValueError(f"ValueError - ip-address: {ip}")
        return ip

    @staticmethod
    def validate_mac_address(mac: str) -> str:
        pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if not re.match(pattern, mac):
            raise ValueError(f"ValueError - mac: {mac}")
        return mac

    @staticmethod
    def validate_port(self, port: int) -> int:
        if port > 9999:
            raise ValueError(f"ValueError - port: {port}")
        return port


validation_helper = ValidationHelper()
