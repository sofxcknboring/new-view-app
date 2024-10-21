
from .base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
from .device import Device
from .switch_excluded_port import SwitchExcludedPort


class Switch(Base):
    """
    Модель для коммутатора.

    Attributes:
        ip_address (str): IP-адрес коммутатора.
        snmp_oid (str): Идентификатор SNMP-агента.
        core_switch_id (int): Уникальный идентификатор опорного коммутатора, к которому принадлежит данный коммутатор.
        core_switch (CoreSwitch): Связанный опорный коммутатор, к которому принадлежит этот коммутатор.
        devices (List[Device]): Список устройств, подключенных к этому коммутатору.
        excluded_ports_relation (List[SwitchExcludedPort]): Список исключенных портов, связанных с данным коммутатором.
    """

    __tablename__ = "switches"

    ip_address: Mapped[str] = mapped_column(unique=True, index=True)
    snmp_oid: Mapped[str] = mapped_column(nullable=False)
    core_switch_id: Mapped[int] = mapped_column(ForeignKey("core_switches.id"))
    core_switch = relationship("CoreSwitch", back_populates="switches")
    devices: Mapped[List["Device"]] = relationship("Device", back_populates="switches")
    excluded_ports_relation: Mapped[List["SwitchExcludedPort"]] = relationship("SwitchExcludedPort",
                                                                               back_populates="switch")