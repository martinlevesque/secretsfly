"""Add environment model

Revision ID: 74ede0b4bd94
Revises: f64a9ca60b41
Create Date: 2023-01-01 13:36:41.813802

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74ede0b4bd94'
down_revision = 'bbef4b28de4b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('environments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('environments')
    # ### end Alembic commands ###