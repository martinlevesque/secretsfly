"""create projects table

Revision ID: bbef4b28de4b
Revises: 
Create Date: 2022-12-25 10:24:03.103563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbef4b28de4b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('project_id', sa.Integer, nullable=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.String(200), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    )



def downgrade() -> None:
    op.drop_table('projects')
