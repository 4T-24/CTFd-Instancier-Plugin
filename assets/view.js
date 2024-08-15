window.instancier = {
    instanciate_button_container: null,
    instanciate_button: null,
    uninstanciate_button: null,
    loading: null,
    deleting: null,
    loaded: null,
    instructions: null,

    last_status: null,
    update_instance_interval: null
}

CTFd._internal.challenge.data = undefined;

// TODO: Remove in CTFd v4.0
CTFd._internal.challenge.renderer = null;

CTFd._internal.challenge.preRender = function() {
    // Clear all intervals
    clearInterval(window.instancier.update_instance_interval);
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

    window.instancier.instanciate_button_container = CTFd.lib.$("#instanciate-button-container");
    window.instancier.instanciate_button = CTFd.lib.$("#instanciate-button");
    window.instancier.uninstanciate_button = CTFd.lib.$("#uninstanciate-button");
    window.instancier.loading = CTFd.lib.$("#instanciate-loading");
    window.instancier.deleting = CTFd.lib.$("#instanciate-deleting");
    window.instancier.loaded = CTFd.lib.$("#instanciate-loaded");
    window.instancier.instructions = CTFd.lib.$("#instance-instructions");

    window.instancier.loading.hide();
    window.instancier.deleting.hide();
    window.instancier.loaded.hide();

    CTFd._internal.challenge.update_instance(true);
    window.instancier.update_instance_interval = setInterval(CTFd._internal.challenge.update_instance, 2500);

    window.instancier.instanciate_button.on("click", function(_event) {
        // grecaptcha.ready(function() {
        //     var recaptcha_token = CTFd.lib.$("#recaptcha-token").val();
        //     grecaptcha.execute(recaptcha_token, { action: 'submit' }).then(function(token) {
                // Send a POST to /api/v1/challenges/<challenge_id>/instance
                CTFd.fetch("/api/v1/challenges/" + challenge_id + "/instance", {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                    },
                    // body: JSON.stringify({
                    //     recaptcha: token
                    // })
                }).then(async function(response) {
                    json = await response.json();
                    CTFd._internal.challenge.status_update(json);
                })
        //     });
        // });
    });

    window.instancier.uninstanciate_button.on("click", function(_event) {
        // Send a DELETE to /api/v1/challenges/<challenge_id>/instance
        // grecaptcha.ready(function() {
        //     var recaptcha_token = CTFd.lib.$("#recaptcha-token").val();
        //     grecaptcha.execute(recaptcha_token, { action: 'submit' }).then(function(token) {
                // Send a DELETE to /api/v1/challenges/<challenge_id>/instance
                CTFd.fetch("/api/v1/challenges/" + challenge_id + "/instance", {
                    method: "DELETE",
                    headers: {
                        Accept: "application/json",
                    },
                    // body: JSON.stringify({
                    //     recaptcha: token
                    // })
                }).then(async function(response) {
                    json = await response.json();
                    CTFd._internal.challenge.status_update(json);
                })
        //     });
        // });
    });

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
};

CTFd._internal.challenge.update_instance = function(force) {
    // check if aria-hidden is set to true
    let challenge_window = CTFd.lib.$("#challenge-window")
    if (challenge_window.attr("aria-hidden") == "true" && !force) {
        clearInterval(window.instancier.update_instance_interval);
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
    if (response.data.status === window.instancier.last_status) {
        return;
    }
    window.instancier.last_status = response.data.status;

    switch (response.data.status) {
        case "Stopped":
            window.instancier.instanciate_button_container.show();
            window.instancier.loading.hide();
            window.instancier.deleting.hide();
            window.instancier.loaded.hide();
            break;
        case "Starting":
            window.instancier.instanciate_button_container.hide();
            window.instancier.loading.show();
            window.instancier.deleting.hide();
            window.instancier.loaded.hide();
            break;
        case "Stopping":
            window.instancier.instanciate_button_container.hide();
            window.instancier.loading.hide();
            window.instancier.deleting.show();
            window.instancier.loaded.hide();
            break;
        case "Running":
            window.instancier.instanciate_button_container.hide();
            window.instancier.loading.hide();
            window.instancier.deleting.hide();
            window.instancier.loaded.show();

            let text = `Instance is running at : `;
            for (let i = 0; i < response.data.servers; i++) {
                server = response.data.servers[i];
                if (i > 0) {
                    text += ", ";
                }

                if (server.kind === "http") {
                    text += `https://${server.host}`;
                } else {
                    text += `${server.host}:${server.port}`;
                }
            }
            window.instancier.instructions.text(text);
            break;
    }
};

// CTFd.lib.$(document).ready(function() {
//     fetch('/api/v1/recaptcha_site_key')
//         .then(response => response.json())
//         .then(d => {
//             let token = d.data.site_key;
//             // add script into the recaptcha div
//             let script = document.createElement('script');
//             script.src = `https://www.google.com/recaptcha/api.js?render=${token}`;
//             document.getElementById('recaptcha').appendChild(script);

//             // update recatcha token input
//             CTFd.lib.$("#recaptcha-token").val(token);
//         });
// });