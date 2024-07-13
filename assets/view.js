CTFd._internal.challenge.data = undefined;

// TODO: Remove in CTFd v4.0
CTFd._internal.challenge.renderer = null;

CTFd._internal.challenge.preRender = function() {
    // Clear all intervals
    clearInterval(window.update_instance_interval);
};

// TODO: Remove in CTFd v4.0
CTFd._internal.challenge.render = null;

CTFd._internal.challenge.postRender = function() {
    CTFd.lib.$(document).ready(function() {
        CTFd._internal.challenge.setup();
    });

};

CTFd._internal.challenge.setup = function() {
    var challenge_id = parseInt(CTFd.lib.$("#challenge-id").val());

    instanciate_button_container = CTFd.lib.$("#instanciate-button-container");
    instanciate_button = CTFd.lib.$("#instanciate-button");
    uninstanciate_button = CTFd.lib.$("#uninstanciate-button");
    loading = CTFd.lib.$("#instanciate-loading");
    loaded = CTFd.lib.$("#instanciate-loaded");
    instructions = CTFd.lib.$("#instance-instructions");

    loading.hide();
    loaded.hide();

    CTFd._internal.challenge.update_instance(true);
    window.update_instance_interval = setInterval(CTFd._internal.challenge.update_instance, 2500);

    instanciate_button.on("click", function(_event) {
        // Send a POST to /api/v1/challenges/<challenge_id>/instance
        CTFd.fetch("/api/v1/challenges/" + challenge_id + "/instance", {
            method: "POST",
            headers: {
                Accept: "application/json",
            }
        }).then(async function(response) {
            json = await response.json();
            CTFd._internal.challenge.status_update(json);
        })
    });

    uninstanciate_button.on("click", function(_event) {
        // Send a DELETE to /api/v1/challenges/<challenge_id>/instance
        CTFd.fetch("/api/v1/challenges/" + challenge_id + "/instance", {
            method: "DELETE",
            headers: {
                Accept: "application/json",
            }
        }).then(async function(response) {
            json = await response.json();
            CTFd._internal.challenge.status_update(json);
        })
    });
};

CTFd._internal.challenge.update_instance = function(force) {
    // check if aria-hidden is set to true
    let challenge_window = CTFd.lib.$("#challenge-window")
    if (challenge_window.attr("aria-hidden") == "true" && !force) {
        clearInterval(window.update_instance_interval);
        return;
    }

    var challenge_id = parseInt(CTFd.lib.$("#challenge-id").val());

    CTFd.fetch("/api/v1/challenges/" + challenge_id + "/instance", {
        method: "GET",
        headers: {
            Accept: "application/json",
        }
    }).then(async function(response) {
        json = await response.json();
        CTFd._internal.challenge.status_update(json);
    })
};

CTFd._internal.challenge.status_update = function(response) {
    switch (response.data.status) {
        case "not_instanciated":
            instanciate_button_container.show();
            loading.hide();
            loaded.hide();
            break;
        case "instanciating":
            instanciate_button_container.hide();
            loading.show();
            loaded.hide();
            break;
        case "instanciated":
            instanciate_button_container.hide();
            loading.hide();
            loaded.show();
            instructions.text("ceci est un exemple d'instruction pour ce connecter");
            break;
    }
};

CTFd._internal.challenge.submit = function(preview) {
    var challenge_id = parseInt(CTFd.lib.$("#challenge-id").val());
    var submission = CTFd.lib.$("#challenge-input").val();

    var body = {
        challenge_id: challenge_id,
        submission: submission
    };
    var params = {};
    if (preview) {
        params["preview"] = true;
    }

    return CTFd.api.post_challenge_attempt(params, body).then(function(response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response;
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response;
        }
        return response;
    });
};