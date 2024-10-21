from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base


class CoreSwitch(Base):
    """Модель для опорного коммутатора.

    Attributes:
        ip_address (str): IP-адрес опорного коммутатора.
        name
        switches (List[Switch]): Список коммутаторов, подключенных к этому опорному коммутатору.
    """

    __tablename__ = "core_switches"

    ip_address: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column(default='Unknown', unique=True, index=True)

    switches: Mapped[List["Switch"]] = relationship("Switch", back_populates="core_switch")


class Switch(Base):
    """
    Модель для коммутатора.

    Attributes:
        ip_address (str): IP-адрес коммутатора.
        core_switch_id (int): Уникальный идентификатор опорного коммутатора, к которому принадлежит данный коммутатор.
        core_switch (CoreSwitch): Связанный опорный коммутатор, к которому принадлежит этот коммутатор.
        devices (List[Device]): Список устройств, подключенных к этому коммутатору.
    """

    __tablename__ = "switches"

    ip_address: Mapped[str] = mapped_column(unique=True, index=True)
    core_switch_id: Mapped[int] = mapped_column(ForeignKey("core_switches.id"))

    core_switch = relationship("CoreSwitch", back_populates="switches")
    devices: Mapped[List["Device"]] = relationship("Device", back_populates="switches")


class Device(Base):
    """
    Модель для устройства.

    Attributes:
        port (int): Номер порта, к которому подключено устройство.
        mac (str): MAC-адрес устройства.
        vlan (int): Идентификатор VLAN, к которому принадлежит устройство.
        ip_address (str): IP-адрес устройства.
        status (bool): Статус устройства (включено/выключено).
        update_time (datetime): Время последнего обновления данных об устройстве.
        switch_id (int): Идентификатор коммутатора, к которому подключено устройство.
        switch (Switch): Связанный коммутатор, к которому принадлежит это устройство.
    """

    __tablename__ = "devices"

    port: Mapped[int] = mapped_column()
    mac: Mapped[str] = mapped_column()
    vlan: Mapped[int] = mapped_column()
    ip_address: Mapped[str] = mapped_column()
    status: Mapped[bool] = mapped_column(default=False)
    update_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    switch_id: Mapped[int] = mapped_column(ForeignKey("switches.id"))
    switch: Mapped["Switch"] = relationship("Switch", back_populates="devices")
