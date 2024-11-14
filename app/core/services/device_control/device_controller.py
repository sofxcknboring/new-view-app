from typing import Optional
from core.config import settings
import winrm


def get_win_user(ip_address: str) -> Optional[str]:
    command = f"quser /server:{ip_address}"

    hostname = f"http://{ip_address}:5985/wsman"
    username = f"NCC\\{settings.winrm.username}"
    password = settings.winrm.password

    session = winrm.Session(hostname, auth=(username, password), transport="ntlm")

    result = session.run_cmd(command)

    decoded_res = result.std_out.decode()

    active_user = ""

    for line in decoded_res.splitlines():
        if "USERNAME" in line or not line.strip():
            continue
        parts = line.split()

        if "Active" in parts:
            active_user = parts[0]
            break

    if active_user:
        return active_user
    return
