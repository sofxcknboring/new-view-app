from abc import ABC, abstractmethod

from .user_info_base import UserInfo


class DeviceControllerBase(ABC):

    def __init__(self, user_info_class: type[UserInfo]):
        self.user_info_class = user_info_class

    @abstractmethod
    def get_info(self):
        pass
