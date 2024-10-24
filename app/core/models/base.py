from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Класс определяет общую структуру для всех моделей, наследующих его.
    Attributes:
        id (Mapped[int]): Уникальный идентификатор,
                          который является первичным ключом для
                          всех наследуемых моделей.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
