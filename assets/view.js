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
    deleting = CTFd.lib.$("#instanciate-deleting");
    loaded = CTFd.lib.$("#instanciate-loaded");
    instructions = CTFd.lib.$("#instance-instructions");

    loading.hide();
    deleting.hide();
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

    // Get submit button
    var submit_button = CTFd.lib.$("#challenge-submit");

    window.instance_challenge_submit = function(response) {
        if (response.data.status === "correct") {
            CTFd.fetch("/api/v1/challenges/" + challenge_id + "/instance", {
                method: "DELETE",
                headers: {
                    Accept: "application/json",
                }
            }).then(async function(response) {
                json = await response.json();
                CTFd._internal.challenge.status_update(json);
            })
        }
    }

    // Change @click.debounce.500ms from submitChallenge to submitChallengeInstance
    submit_button.attr("x-on:click.debounce.500ms", "submitChallenge().then(() => window.instance_challenge_submit(response));");
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
            deleting.hide();
            loaded.hide();
            break;
        case "instanciating":
            instanciate_button_container.hide();
            loading.show();
            deleting.hide();
            loaded.hide();
            break;
        case "deleting":
            instanciate_button_container.hide();
            loading.hide();
            deleting.show();
            loaded.hide();
            break;
        case "instanciated":
            instanciate_button_container.hide();
            loading.hide();
            deleting.hide();
            loaded.show();
            instructions.text(response.data.instructions);
            break;
    }
};