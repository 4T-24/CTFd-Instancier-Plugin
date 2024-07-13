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
        "instanciated_challenge",
        sqlalchemy.Column("id", sqlalchemy.Integer(), nullable=False),
        sqlalchemy.Column("challenge_slug",
                          sqlalchemy.String(32), nullable=False),
        sqlalchemy.ForeignKeyConstraint(["id"], ["challenges.id"]),
        sqlalchemy.PrimaryKeyConstraint("id"),
    )

    try:
        if url.startswith("mysql"):
            op.drop_constraint(
                "instanciated_challenge_ibfk_1", "instanciated_challenge", type_="foreignkey"
            )
        elif url.startswith("postgres"):
            op.drop_constraint(
                "instanciated_challenge_id_fkey", "instanciated_challenge", type_="foreignkey"
            )
    except sqlalchemy.exc.InternalError as e:
        print(str(e))

    try:
        op.create_foreign_key(
            None, "instanciated_challenge", "challenges", ["id"], ["id"], ondelete="CASCADE"
        )
    except sqlalchemy.exc.InternalError as e:
        print(str(e))


def downgrade(op=None):
    bind = op.get_bind()
    url = str(bind.engine.url)
    try:
        if url.startswith("mysql"):
            op.drop_constraint(
                "instanciated_challenge_ibfk_1", "instanciated_challenge", type_="foreignkey"
            )
        elif url.startswith("postgres"):
            op.drop_constraint(
                "instanciated_challenge_id_fkey", "instanciated_challenge", type_="foreignkey"
            )
    except sqlalchemy.exc.InternalError as e:
        print(str(e))

    try:
        op.create_foreign_key(None, "instanciated_challenge+",
                              "challenges", ["id"], ["id"])
    except sqlalchemy.exc.InternalError as e:
        print(str(e))
