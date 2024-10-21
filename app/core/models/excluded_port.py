from .base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
from .switch_excluded_port import SwitchExcludedPort



class ExcludedPort(Base):
    """
    Модель для исключенного порта.

    Attributes:
        port_number (int): Номер исключенного порта.(Порт должен быть уникальным)
        switches (List[Switch]): Список коммутаторов, к которым принадлежит этот исключенный порт.
    """

    __tablename__ = "excluded_ports"

    port_number: Mapped[int] = mapped_column(unique=True)

    switches: Mapped[List["SwitchExcludedPort"]] = relationship("SwitchExcludedPort", back_populates="excluded_port")