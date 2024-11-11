import re
from ipaddress import ip_address
from typing import Any


class ValidationHelper:
    @staticmethod
    def validate_core_switch_oid(oid: str) -> str:
        pattern = r"^1\.3\.6\.1\.2\.1\.4\.22\.(0|9|\d).(0|9|\d)$"
        if not re.match(pattern, oid):
            raise ValueError(f"ValueError - OID: {oid}. Check DOCs. OID must 1.3.6.1.2.1.4.22.1.2")
        return oid

    @staticmethod
    def validate_switch_oid(oid: str) -> str:
        pattern = r"^1\.3\.6\.1\.2\.1\.17\.7\.1\.2\.2\.1\.2$"
        if not re.match(pattern, oid):
            raise ValueError(f"ValueError - OID: {oid}. Check DOCs OID must be 1.3.6.1.2.1.17.7.1.2.2.1.2")
        return oid

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
    def validate_port(port: Any) -> int:
        try:
            return int(port)
        except ValueError:
            raise ValueError(f"Not valid data: port - {port}")


validation_helper = ValidationHelper()
