from xml.etree import ElementTree

import paramiko
from core.config import settings

from .device_controller_base import DeviceControllerBase
from .user_info_base import UserInfo


class LinUserInfo(UserInfo):
    def __init__(self, domain_user, pc_name, nau_user, remote_control):
        self.domain_user = domain_user
        self.pc_name = pc_name
        self.remote_control = remote_control
        self.nau_user = nau_user

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


class LinDeviceController(DeviceControllerBase):

    def __init__(self, ip_address, user_info_class):
        super().__init__(user_info_class)
        self.username = settings.ssh.username
        self.password = settings.ssh.password
        self.ip_address = ip_address
        self.session = self.__create_session()

    def __create_session(self):

        try:
            session = paramiko.SSHClient()
            session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            session.connect(
                hostname=self.ip_address, username=self.username, password=self.password, port=22, timeout=5
            )
            return session
        except Exception:
            raise

    def get_info(self):
        lin_info = {}
        if self.session:
            # domain_user
            stdin, stdout, stderr = self.session.exec_command("id -u -n")
            domain_user = stdout.read().decode("utf-8").strip()
            lin_info["domain_user"] = domain_user

            # pc_name
            stdin, stdout, stderr = self.session.exec_command("uname")
            pc_name = stdout.read().decode("utf-8").strip()
            lin_info["pc_name"] = pc_name

            # remote_control
            stdin, stdout, stderr = self.session.exec_command("rustdesk --get-id")
            rust_desk_id = stdout.read().decode("utf-8").strip()
            lin_info["remote_control"] = rust_desk_id

            # nau_user
            stdin, stdout, stderr = self.session.exec_command("cat /home/newcontact/.nausoftphone/nauserver.config")
            nau_user = stdout.read().decode("utf-8")
            root = ElementTree.fromstring(nau_user)
            for line in root.findall("PROPERTY"):
                if line.get("name") == "Login":
                    try:
                        lin_info["nau_user"] = line.text.strip()
                    except Exception:
                        lin_info["nau_user"] = "User not found"
                    break

            self.session.close()
            print(lin_info)

            # Создание объекта LinUserInfo
            return self.user_info_class.new_device(lin_info)
        else:
            return None
