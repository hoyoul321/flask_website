"""empty message

Revision ID: f5c5a18a3d38
Revises: 4f9d38167d87
Create Date: 2021-04-26 16:33:19.453793

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import context

# revision identifiers, used by Alembic.
revision = 'f5c5a18a3d38'
down_revision = '4f9d38167d87'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

def upgrade_AUDIT():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_AUDIT():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


