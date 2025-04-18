"""Add weekly goals model

Revision ID: 32275fda8e55
Revises: 3e2cd2cc3ce3
Create Date: 2025-04-07 09:20:52.767910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32275fda8e55'
down_revision = '3e2cd2cc3ce3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('weekly_goals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('week_start', sa.Date(), nullable=False),
    sa.Column('content', sa.String(length=500), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('week_start')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('weekly_goals')
    # ### end Alembic commands ###
