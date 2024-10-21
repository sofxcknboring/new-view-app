from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base

from .switch import Switch


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
