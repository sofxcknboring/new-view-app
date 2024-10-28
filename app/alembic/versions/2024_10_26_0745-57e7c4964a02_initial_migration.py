"""Initial migration

Revision ID: 57e7c4964a02
Revises: 
Create Date: 2024-10-26 07:45:29.220127

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "57e7c4964a02"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "switch_excluded_ports",
        sa.Column("switch_id", sa.Integer(), nullable=False),
        sa.Column("excluded_port_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["excluded_port_id"],
            ["excluded_ports.id"],
        ),
        sa.ForeignKeyConstraint(
            ["switch_id"],
            ["switches.id"],
        ),
        sa.PrimaryKeyConstraint("switch_id", "excluded_port_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("switch_excluded_ports")
    # ### end Alembic commands ###
