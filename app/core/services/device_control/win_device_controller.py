from xml.etree import ElementTree

import winrm
from core.config import settings

from .device_controller_base import DeviceControllerBase
from .user_info_base import UserInfo


class WinUserInfo(UserInfo):
    def __init__(self, domain_user, pc_name, nau_user, remote_control):
        self.domain_user = domain_user
        self.pc_name = pc_name
        self.remote_control = remote_control
        self.nau_user = nau_user
        print(repr(self))

    @classmethod
    def new_device(cls, device: dict):
        return cls(**device)

    def to_dict(self):
        return {
            "domain_user": self.domain_user,
            "pc_name": self.pc_name,
            "remote_control": self.remote_control,
            "nau_user": self.nau_user,
        }


class WinDeviceController(DeviceControllerBase):
    def __init__(self, ip_address, user_info_class):
        super().__init__(user_info_class)
        self.hostname = f"http://{ip_address}:5985/wsman"
        self.username = f"NCC\\{settings.winrm.username}"
        self.__password = settings.winrm.password
        self.session = self.__create_session()
        self.ip_address = ip_address

    def __create_session(self):
        try:
            session = winrm.Session(self.hostname, auth=(self.username, self.__password), transport="ntlm")
            return session
        except Exception:
            raise

    def get_info(self):
        if self.session:
            win_info = {}
            active_user = False

            domain_user_result = self.session.run_cmd(f"quser /server:{self.ip_address}")
            decoded_domain_user = domain_user_result.std_out.decode("utf-8")

            for line in decoded_domain_user.splitlines():
                if "USERNAME" in line or not line.strip():
                    continue
                parts = line.split()

                if "Active" in parts:
                    win_info["domain_user"] = parts[0].strip()
                    active_user = True
                    break

            if active_user:
                pc_name_result = self.session.run_cmd("hostname")
                win_info["pc_name"] = pc_name_result.std_out.decode("utf-8").strip()

                rust_desk_path = "C:\\Program Files\\RustDesk\\rustdesk.exe"
                cmd_rd_id = f"& '{rust_desk_path}' --get-id | out-host"
                rd_result = self.session.run_ps(cmd_rd_id)
                win_info["remote_control"] = rd_result.std_out.decode("utf-8").strip()

                cmd_nau_user = (
                    f"type C:\\Users\\{win_info['domain_user']}\\AppData\\Roaming\\nausoftphone\\nauserver.config"
                )
                nau_user_result = self.session.run_cmd(cmd_nau_user)
                decoded_nau_user = nau_user_result.std_out.decode("utf-8")

                root = ElementTree.fromstring(decoded_nau_user)
                for line in root.findall("PROPERTY"):
                    if line.get("name") == "Login":
                        win_info["nau_user"] = line.text.strip()
                        break
                return self.user_info_class.new_device(win_info)
            else:
                print("Нет активного пользователя.")
                return None
        else:
            return None
