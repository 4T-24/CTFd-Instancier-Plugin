from flask import Blueprint

from CTFd.models import Challenges, db
from CTFd.plugins.dynamic_challenges import DynamicChallenge
from CTFd.plugins.dynamic_challenges.decay import DECAY_FUNCTIONS, logarithmic
from CTFd.plugins.challenges import BaseChallenge
from urllib.parse import urljoin
from CTFd.utils.user import (
    authed,
    get_current_team,
    get_current_user,
    is_admin,
)
from CTFd.utils import config
from requests import get
from .store import retrieve

class IDynamicChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "i_dynamic"}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)
    function = db.Column(db.String(32), default="logarithmic")
    slug = db.Column(db.String(32))
    is_instanced = db.Column(db.Boolean, default=False)
    has_oracle = db.Column(db.Boolean, default=False)
    
    def __init__(self, *args, **kwargs):
        super(IDynamicChallenge, self).__init__(**kwargs)
        self.value = kwargs["initial"]


class IDynamicValueChallenge(BaseChallenge):
    id = "i_dynamic"  # Unique identifier used to register challenges
    name = "i_dynamic"  # Name of a challenge type
    templates = (
        {  # Handlebars templates used for each aspect of challenge editing & viewing
            "create": "/plugins/i_challenges/assets/create.html",
            "update": "/plugins/i_challenges/assets/update.html",
            "view": "/plugins/i_challenges/assets/view.html",
        }
    )
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/i_challenges/assets/create.js",
        "update": "/plugins/i_challenges/assets/update.js",
        "view": "/plugins/i_challenges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/i_challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "i_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = IDynamicChallenge

    @classmethod
    def calculate_value(cls, challenge):
        f = DECAY_FUNCTIONS.get(challenge.function, logarithmic)
        value = f(challenge)

        challenge.value = value
        db.session.commit()
        return challenge

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = IDynamicChallenge.query.filter_by(id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "slug": challenge.slug,
            "value": challenge.value,
            "initial": challenge.initial,
            "decay": challenge.decay,
            "minimum": challenge.minimum,
            "function": challenge.function,
            "description": challenge.description,
            "connection_info": challenge.connection_info,
            "next_id": challenge.next_id,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "is_instanced": challenge.is_instanced,
            "has_oracle": challenge.has_oracle,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
                "slug": challenge.slug,
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
            # We need to set these to floats so that the next operations don't operate on strings
            if attr in ("initial", "minimum", "decay"):
                value = float(value)
            setattr(challenge, attr, value)

        return IDynamicValueChallenge.calculate_value(challenge)

    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)

        IDynamicValueChallenge.calculate_value(challenge)
    
    @classmethod
    def attempt(cls, challenge, request):
        app = retrieve("app")
        token = app.config.get("4TS_INSTANCER_TOKEN")
        headers={"X-Ctfd-Auth": token}
        challenge = IDynamicChallenge.query.filter_by(id=challenge.id).first()

        
        user = get_current_user()
        instance_id = user.id

        # Check if this is an oracle challenge
        if challenge.has_oracle:
            data = request.form or request.get_json()
            submission = data["submission"].strip()
            if submission == "":
                uri = urljoin(app.config.get("4TS_INSTANCER_BASE_URL"), f"/api/v1/{challenge.slug}/{instance_id}/is_solved")
                try:
                    response = get(uri, headers=headers)
                    if "true" in response.text:
                        return True, "Challenge is solved !"
                    else:
                        return False, "Challenge is not solved"
                except:
                    return False, "Failed to fetch status of challenge"
            else:
                return False, "Nuh-Uh"
            