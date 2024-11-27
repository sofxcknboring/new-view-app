from abc import ABC, abstractmethod


class UserInfo(ABC):

    @classmethod
    @abstractmethod
    def new_device(cls, *args, **kwargs):
        pass
