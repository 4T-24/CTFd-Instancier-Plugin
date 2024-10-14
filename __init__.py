from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.migrations import upgrade

from .api import api_routes
from .config import config
from .models import IDynamicValueChallenge
from .store import store

def load(app):
    config(app)

    store("app", app)
    
    upgrade(plugin_name="i_challenges")
    
    # Register our classes
    # CHALLENGE_CLASSES["i_static"] = IDynamicValueChallenge
    CHALLENGE_CLASSES["i_dynamic"] = IDynamicValueChallenge
    
    register_plugin_assets_directory(
        app, base_path="/plugins/i_challenges/assets/"
    )

    api_routes(app)
