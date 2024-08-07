"""Agregué una nueva columna en la tabla de usuarios llamada google_access_token para almacenar los tokens de acceso de google

Revision ID: 480508d77175
Revises: 
Create Date: 2024-06-16 21:20:03.769462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '480508d77175'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('google_access_token', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'google_access_token')
    # ### end Alembic commands ###
