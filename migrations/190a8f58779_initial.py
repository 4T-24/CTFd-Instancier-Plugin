"""Add cascading delete to instanciated challenges

Revision ID: 190a8f58779
Revises:

"""
import sqlalchemy

revision = "190a8f58779"
down_revision = None
branch_labels = None
depends_on = None


def upgrade(op=None):
    bind = op.get_bind()
    url = str(bind.engine.url)

    op.create_table(
        "i_dynamic_challenge",
        sqlalchemy.Column("id", sqlalchemy.Integer(), nullable=False),
        sqlalchemy.Column("initial", sqlalchemy.Integer(), nullable=True),
        sqlalchemy.Column("minimum", sqlalchemy.Integer(), nullable=True),
        sqlalchemy.Column("decay", sqlalchemy.Integer(), nullable=True),
        sqlalchemy.Column("slug", sqlalchemy.String(32), nullable=False),
        sqlalchemy.Column("function", sqlalchemy.String(32), nullable=False),
        sqlalchemy.Column("is_instanced", sqlalchemy.Boolean, nullable=False),
        sqlalchemy.Column("has_oracle", sqlalchemy.Boolean, nullable=False),
        sqlalchemy.ForeignKeyConstraint(["id"], ["challenges.id"], ondelete="CASCADE"),
        sqlalchemy.PrimaryKeyConstraint("id"),
    )


def downgrade(op=None):
    bind = op.get_bind()
    url = str(bind.engine.url)
    
    op.drop_table("i_dynamic_challenge")