"""Add secrets model

Revision ID: 613ddd9d4860
Revises: 494010461397
Create Date: 2023-01-07 16:47:54.760798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '613ddd9d4860'
down_revision = '494010461397'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('secrets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('environment_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('comment', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['environment_id'], ['environments.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id', 'environment_id', 'name')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('secrets')
    # ### end Alembic commands ###
