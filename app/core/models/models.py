from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base


class CoreSwitch(Base):
    """Модель для опорного коммутатора.

    Attributes:
        ip_address (str): IP-адрес опорного коммутатора.
        name (str): Комментарий или название, если это необходимо.
        snmp_oid (str): Идентификатор SNMP-агента.
        switches (List[Switch]): Список коммутаторов, подключенных к этому опорному коммутатору.
    """

    __tablename__ = "core_switches"

    ip_address: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, index=True, nullable=True)
    snmp_oid: Mapped[str] = mapped_column(nullable=False)

    switches: Mapped[List["Switch"]] = relationship("Switch", back_populates="core_switch")


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


class SwitchExcludedPort(Base):
    """
    Промежуточная модель для связи между коммутатором и исключенными портами.

    Attributes:
        switch_id (int): ID коммутатора.
        excluded_port_id (int): ID исключенного порта.
    """

    __tablename__ = "switch_excluded_ports"

    switch_id: Mapped[int] = mapped_column(ForeignKey("switches.id"), primary_key=True)
    excluded_port_id: Mapped[int] = mapped_column(ForeignKey("excluded_ports.id"), primary_key=True)

    switch: Mapped["Switch"] = relationship("Switch", back_populates="excluded_ports_relation")
    excluded_port: Mapped["ExcludedPort"] = relationship("ExcludedPort", back_populates="switches")




class Device(Base):
    """
    Модель для устройства.

    Attributes:
        workplace_number: Номер рабочего места.(по умолчанию null)
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

    workplace_number: Mapped[str] = mapped_column(unique=True, nullable=True)
    port: Mapped[int] = mapped_column()
    mac: Mapped[str] = mapped_column()
    vlan: Mapped[int] = mapped_column()
    ip_address: Mapped[str] = mapped_column()
    status: Mapped[bool] = mapped_column(default=False)
    update_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    switch_id: Mapped[int] = mapped_column(ForeignKey("switches.id"))
    switch: Mapped["Switch"] = relationship("Switch", back_populates="devices")
