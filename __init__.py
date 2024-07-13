from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.migrations import upgrade

from .api import api_routes
from .config import config
from .models import InstanciatedValueChallenge

def load(app):
    config(app)
    
    upgrade(plugin_name="instanciated_challenges")
    CHALLENGE_CLASSES["instanciated"] = InstanciatedValueChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/instanciated_challenges/assets/"
    )

    api_routes(app)
