from .base import Base


from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .switch import Switch
from .excluded_port import ExcludedPort




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