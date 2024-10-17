from flask import render_template
from flask import abort, request, render_template, url_for
from CTFd.models import Challenges
from CTFd.models import Fails, Hints, HintUnlocks, Solves, Submissions, db
from CTFd.schemas.tags import TagSchema
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils import config
from flask_restx import Resource
from CTFd.utils import user as current_user, get_config
from sqlalchemy.sql import and_
from CTFd.utils.security.signing import serialize
from CTFd.utils.dates import isoformat, unix_time_to_utc, ctf_ended, ctftime
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
from CTFd.utils.logging import log
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

from .models import IDynamicChallenge

def api_routes(app):
    # recaptcha_site_key = app.config.get("4TS_INSTANCER_RECAPTCHA_SITE_KEY")
    
    # @app.route("/api/v1/recaptcha_site_key", methods=['GET'])
    # def get_recaptcha_site_key():
    #     return {"success": True, "data": {"site_key": recaptcha_site_key}}

    token = app.config.get("4TS_INSTANCER_TOKEN")
    headers={"X-Ctfd-Auth": token}
    
    @app.route("/api/v1/challenges/<challenge_id>/instance", methods=['GET', 'POST', 'DELETE'])
    # @check_challenge_visibility
    # @during_ctf_time_only
    # @require_verified_emails
    def handle_routes(challenge_id):
        if request.method == 'GET':
            return get_instance(challenge_id)
        elif request.method == 'POST':
            return start_instance(challenge_id)
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
        
        # Get instanciated Challenge
        instanciated_challenge = IDynamicChallenge.query.filter_by(id=challenge_id).first()

        # Send request to instancer service at /api/v1/instanciate
        uri = urljoin(app.config.get("4TS_INSTANCER_BASE_URL"), f"/api/v1/{instanciated_challenge.slug}/{instance_id}")

        try:
            response = get(uri, headers=headers)
            return {"success": True, "data": response.json()}
        except:
            # Log error
            app.logger.error(f"Failed to get instance for challenge {challenge_id} with status code {response.status_code}")
            return {"success": False}


    def start_instance(challenge_id):
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

        # Get instanciated Challenge
        instanciated_challenge = IDynamicChallenge.query.filter_by(id=challenge_id).first()

        if not instanciated_challenge.is_instanced:
            return {"success": False, "message": "This challenge is not instanced"}
        
        # Send request to instancer service at /api/v1/instanciate
        try:
            response = post(
                urljoin(app.config.get("4TS_INSTANCER_BASE_URL"), f"/api/v1/{instanciated_challenge.slug}/{instance_id}"),
                headers=headers,
                # json=request.json
            ).json()
            
            return {"success": True, "data": response}
        except:
            # Log error
            app.logger.error(f"Failed to start instance for challenge {challenge_id} with status code {response.status_code}")
            return {"success": False}



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

        # Get instanciated Challenge
        instanciated_challenge = IDynamicChallenge.query.filter_by(id=challenge_id).first()
        
        # Send request to instancer service at /api/v1/instanciate
        try:
            response = delete(
                urljoin(app.config.get("4TS_INSTANCER_BASE_URL"), f"/api/v1/{instanciated_challenge.slug}/{instance_id}"),
                headers=headers,
                # json=request.json
            ).json()

            return {"success": True, "data": response}
        except:
            # Log error
            app.logger.error(f"Failed to stop instance for challenge {challenge_id} with status code {response.status_code}")
            return {"success": False}
    
    @app.route("/api/v1/date", methods=['GET'])
    def get_ctf_date():
        ctf_start = config.get_config("start")
        if ctf_start:
            ctf_start = isoformat(unix_time_to_utc(int(ctf_start)))

        ctf_end = config.get_config("end")
        if ctf_end:
            ctf_end = isoformat(unix_time_to_utc(int(ctf_end)))

        ctf_freeze = config.get_config("freeze")
        if ctf_freeze:
            ctf_freeze = isoformat(unix_time_to_utc(int(ctf_freeze)))

        return {"success": True, "data": {"start": ctf_start, "end": ctf_end, "freeze": ctf_freeze}}
