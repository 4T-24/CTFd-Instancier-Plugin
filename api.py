from flask import render_template
from flask import abort, request, render_template, url_for
from CTFd.models import Challenges
from CTFd.models import Hints, HintUnlocks, Solves, Submissions, db
from CTFd.schemas.tags import TagSchema
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils import config
from flask_restx import Resource
from sqlalchemy.sql import and_
from CTFd.utils.security.signing import serialize
from CTFd.utils.dates import ctf_ended
from CTFd.utils.challenges import (
    get_solve_counts_for_challenges,
    get_solve_ids_for_user_id,
)
from CTFd.utils.decorators.visibility import (
    check_challenge_visibility,
)
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_verified_emails,
)
from CTFd.utils.user import (
    authed,
    get_current_team,
    get_current_user,
    is_admin,
)
from CTFd.utils.config.visibility import (
    accounts_visible,
    challenges_visible,
    scores_visible,
)

from requests import get, post, delete
from urllib.parse import urljoin

def api_routes(app):
    instancer_token = app.config.get("4TS_INSTANCER_TOKEN")
    
    
    @app.route("/api/v1/challenges/<challenge_id>/instance", methods=['GET', 'POST', 'DELETE'])
    # @check_challenge_visibility
    # @during_ctf_time_only
    # @require_verified_emails
    def handle_routes(challenge_id):
        if request.method == 'GET':
            return get_instance(challenge_id)
        elif request.method == 'POST':
            return get_instance(challenge_id)
        elif request.method == 'DELETE':
            return stop_instance(challenge_id)
        else:
            abort(405)
    
    def get_instance(challenge_id):
        if not authed():
            abort(403)

        if is_admin():
            chal = Challenges.query.filter(
                Challenges.id == challenge_id).first_or_404()
        else:
            chal = Challenges.query.filter(
                Challenges.id == challenge_id,
                and_(Challenges.state != "hidden",
                        Challenges.state != "locked"),
            ).first_or_404()

        try:
            chal_class = get_chal_class(chal.type)
        except KeyError:
            abort(
                500,
                f"The underlying challenge type ({chal.type}) is not installed. This challenge can not be loaded.",
            )

        user = get_current_user()
        instance_id = user.id
        # Check if CTFd is in team mode, if so, get the team's id
        if config.is_teams_mode():
            team = get_current_team()
            instance_id = team.id

        # Send request to instancer service at /api/v1/instanciate
        uri = urljoin(app.config.get("4TS_INSTANCER_BASE_URL"), f"/p9yv9f6/api/v1/{challenge_id}/{instance_id}")
        response = get(uri, headers={"Authorization": f"Bearer {instancer_token}"})

        return {"success": True, "data": response.json()}


    def start_instance(challenge_id):
        if not authed():
            print("Not authed")
            abort(403)

        if is_admin():
            chal = Challenges.query.filter(
                Challenges.id == challenge_id).first_or_404()
        else:
            chal = Challenges.query.filter(
                Challenges.id == challenge_id,
                and_(Challenges.state != "hidden",
                        Challenges.state != "locked"),
            ).first_or_404()

        try:
            chal_class = get_chal_class(chal.type)
        except KeyError:
            abort(
                500,
                f"The underlying challenge type ({chal.type}) is not installed. This challenge can not be loaded.",
            )

        user = get_current_user()
        instance_id = user.id
        # Check if CTFd is in team mode, if so, get the team's id
        if config.is_teams_mode():
            team = get_current_team()
            instance_id = team.id

        # Send request to instancer service at /api/v1/instanciate
        response = post(
            urljoin(app.config.get("4TS_INSTANCER_BASE_URL"), f"/p9yv9f6/api/v1/{challenge_id}/{instance_id}"),
            headers={"Authorization": f"Bearer {instancer_token}"},
        ).json()

        return {"success": True, "data": response}


    def stop_instance(challenge_id):
        if not authed():
            abort(403)

        if is_admin():
            chal = Challenges.query.filter(
                Challenges.id == challenge_id).first_or_404()
        else:
            chal = Challenges.query.filter(
                Challenges.id == challenge_id,
                and_(Challenges.state != "hidden",
                        Challenges.state != "locked"),
            ).first_or_404()

        try:
            chal_class = get_chal_class(chal.type)
        except KeyError:
            abort(
                500,
                f"The underlying challenge type ({chal.type}) is not installed. This challenge can not be loaded.",
            )

        user = get_current_user()
        instance_id = user.id
        # Check if CTFd is in team mode, if so, get the team's id
        if config.is_teams_mode():
            team = get_current_team()
            instance_id = team.id

        # Send request to instancer service at /api/v1/instanciate
        response = delete(
            urljoin(app.config.get("4TS_INSTANCER_BASE_URL"), f"/api/v1/{challenge_id}/{instance_id}"),
            headers={"Authorization": f"Bearer {instancer_token}"},
        ).json()

        return {"success": True, "data": response}