from flask import Blueprint

from CTFd.models import Challenges, db
from CTFd.plugins.challenges import BaseChallenge

class InstanciatedChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "instanciated"}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    challenge_slug = db.Column(db.String(32), default=0)

    def __init__(self, *args, **kwargs):
        super(InstanciatedChallenge, self).__init__(**kwargs)


class InstanciatedValueChallenge(BaseChallenge):
    id = "instanciated"  # Unique identifier used to register challenges
    name = "instanciated"  # Name of a challenge type
    templates = (
        {  # Handlebars templates used for each aspect of challenge editing & viewing
            "create": "/plugins/instanciated_challenges/assets/create.html",
            "update": "/plugins/instanciated_challenges/assets/update.html",
            "view": "/plugins/instanciated_challenges/assets/view.html",
        }
    )
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/instanciated_challenges/assets/create.js",
        "update": "/plugins/instanciated_challenges/assets/update.js",
        "view": "/plugins/instanciated_challenges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/instanciated_challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "instanciated_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = InstanciatedChallenge

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = InstanciatedChallenge.query.filter_by(
            id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "description": challenge.description,
            "connection_info": challenge.connection_info,
            "next_id": challenge.next_id,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
        return data

    @classmethod
    def update(cls, challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()
        for attr, value in data.items():
            setattr(challenge, attr, value)

        db.session.commit()
        return challenge

    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)

