"""update_tables

Revision ID: ec3ef9e57d2d
Revises: c69ad7c2b385
Create Date: 2024-10-22 00:27:19.007985

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ec3ef9e57d2d"
down_revision: Union[str, None] = "c69ad7c2b385"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "excluded_ports",
        sa.Column("port_number", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("port_number"),
    )
    op.create_table(
        "switch_excluded_ports",
        sa.Column("switch_id", sa.Integer(), nullable=False),
        sa.Column("excluded_port_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["excluded_port_id"],
            ["excluded_ports.id"],
        ),
        sa.ForeignKeyConstraint(
            ["switch_id"],
            ["switches.id"],
        ),
        sa.PrimaryKeyConstraint("switch_id", "excluded_port_id", "id"),
    )
    op.add_column(
        "core_switches", sa.Column("snmp_oid", sa.String(), nullable=False)
    )
    op.alter_column(
        "core_switches", "name", existing_type=sa.VARCHAR(), nullable=True
    )
    op.add_column(
        "devices", sa.Column("workplace_number", sa.String(), nullable=True)
    )
    op.create_unique_constraint(None, "devices", ["workplace_number"])
    op.add_column(
        "switches", sa.Column("snmp_oid", sa.String(), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("switches", "snmp_oid")
    op.drop_constraint(None, "devices", type_="unique")
    op.drop_column("devices", "workplace_number")
    op.alter_column(
        "core_switches", "name", existing_type=sa.VARCHAR(), nullable=False
    )
    op.drop_column("core_switches", "snmp_oid")
    op.drop_table("switch_excluded_ports")
    op.drop_table("excluded_ports")
    # ### end Alembic commands ###
