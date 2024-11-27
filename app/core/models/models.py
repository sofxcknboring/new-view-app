from datetime import datetime
from typing import List

from core.models.base import Base
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Location(Base):

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    prefix: Mapped[str] = mapped_column(unique=True, index=True)

    core_switches: Mapped[List["CoreSwitch"]] = relationship("CoreSwitch", back_populates="location", lazy="selectin")
    switches: Mapped[List["Switch"]] = relationship("Switch", back_populates="location", lazy="selectin")


class CoreSwitch(Base):

    __tablename__ = "core_switches"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str] = mapped_column(unique=True, index=True, nullable=True)
    ip_address: Mapped[str] = mapped_column(unique=True, index=True)
    snmp_oid: Mapped[str] = mapped_column(default="1.3.6.1.2.1.4.22.1.2")

    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    location: Mapped["Location"] = relationship("Location", back_populates="core_switches", lazy="selectin")

    switches: Mapped[List["Switch"]] = relationship("Switch", back_populates="core_switch", lazy="selectin")


class Switch(Base):

    __tablename__ = "switches"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip_address: Mapped[str] = mapped_column(unique=True, index=True)

    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    location: Mapped["Location"] = relationship("Location", back_populates="switches", lazy="selectin")

    comment: Mapped[str] = mapped_column(nullable=True)
    snmp_oid: Mapped[str] = mapped_column(default="1.3.6.1.2.1.17.7.1.2.2.1.2")

    core_switch_ip: Mapped[str] = mapped_column(ForeignKey("core_switches.ip_address"))
    core_switch = relationship("CoreSwitch", back_populates="switches", lazy="selectin")

    devices: Mapped[List["Device"]] = relationship("Device", back_populates="switch", lazy="selectin")
    ports_relation: Mapped[List["SwitchPort"]] = relationship("SwitchPort", back_populates="switch", lazy="selectin")


class Port(Base):

    __tablename__ = "ports"

    id: Mapped[int] = mapped_column(primary_key=True)
    port_number: Mapped[int] = mapped_column(unique=True)
    comment: Mapped[str] = mapped_column(nullable=True)

    switches: Mapped[List["SwitchPort"]] = relationship("SwitchPort", back_populates="port", lazy="selectin")


class SwitchPort(Base):

    __tablename__ = "switch_ports"

    switch_id: Mapped[int] = mapped_column(ForeignKey("switches.id"), primary_key=True)
    port_id: Mapped[int] = mapped_column(ForeignKey("ports.id"), primary_key=True)

    switch: Mapped["Switch"] = relationship("Switch", back_populates="ports_relation", lazy="selectin")
    port: Mapped["Port"] = relationship("Port", back_populates="switches", lazy="selectin")


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    workplace_number: Mapped[str] = mapped_column(unique=True, nullable=True)
    port: Mapped[int] = mapped_column()
    mac: Mapped[str] = mapped_column(unique=True)
    ip_address: Mapped[str] = mapped_column()
    pc_name: Mapped[str] = mapped_column(nullable=True)
    nau_user: Mapped[str] = mapped_column(nullable=True)
    domain_user: Mapped[str] = mapped_column(nullable=True)
    remote_control: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[bool] = mapped_column(default=False)
    update_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    switch_id: Mapped[int] = mapped_column(ForeignKey("switches.id"))
    switch: Mapped["Switch"] = relationship("Switch", back_populates="devices", lazy="selectin")

    vlan_id: Mapped[int] = mapped_column(ForeignKey("vlans.id"))
    vlan: Mapped["Vlan"] = relationship("Vlan", back_populates="devices", lazy="selectin")


class Vlan(Base):
    __tablename__ = "vlans"

    id: Mapped[int] = mapped_column(primary_key=True)
    vlan: Mapped[int] = mapped_column(unique=True)
    comment: Mapped[str] = mapped_column(nullable=True)

    devices: Mapped[List["Device"]] = relationship("Device", back_populates="vlan", lazy="selectin")
