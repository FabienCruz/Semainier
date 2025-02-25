"""Initial migration - create tables List, Sublist, Activity

Revision ID: e3a23cd410ac
Revises: 
Create Date: 2025-02-26 10:14:18.805638

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3a23cd410ac'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('list_id', sa.Integer(), nullable=False),
    sa.Column('sublist_id', sa.Integer(), nullable=True),
    sa.Column('duration', sa.Enum('SMALL', 'MEDIUM', 'LARGE', name='durationsize'), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('start_time', sa.Time(), nullable=True),
    sa.Column('is_template', sa.Boolean(), nullable=True),
    sa.Column('is_priority', sa.Boolean(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_completed', sa.Boolean(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sublist_id'], ['sublists.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('activities')
    # ### end Alembic commands ###
