from .base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List

from switch import Switch

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