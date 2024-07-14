# 4T$'s CTFd Instancier

Plugin that connects to an Instancier compatible API in order to instanciate challenges on CTFd.
If the CTF is team based, instances will be per team.

## Installation

- To install clone this repository to the [CTFd/plugins](https://github.com/CTFd/CTFd/tree/master/CTFd/plugins) folder.
- Add the following values as environment variables or edit [CTFd/config.py](https://github.com/CTFd/CTFd/blob/master/CTFd/config.py) to add the following entries:
 - `4TS_INSTANCER_BASE_URL`: The base URI leading to your Instancier API
 - `4TS_INSTANCER_TOKEN`: A secret token to communicate with the Instancier API.
 - `4TS_INSTANCER_RECAPTCHA_SITE_KEY`: The recaptcha site key to avoid instance spam.

## Instancier API

`slug` is defined when creating an instanciated challenge, the instancier api should know this slug beforehand.
`instance_id` can be the `user_id` or the `team_id` depending on the CTFd gamemode.

- `GET /api/v1/{slug}/{instance_id}` : Get the current status
- `POST /api/v1/{slug}/{instance_id}` : Trigger instanciation, response is the status
- `DELETE /api/v1/{slug}/{instance_id}` : Trigger deletion, response is the status

The API must response with this following schema :

```json
{
    "status": "Stopped / Starting / Stopping / Running",
    "server": {
        "kind": "http / tcp",
        "host": "google.com",
        "port": "optional"
    }
}
```

`port` is only set for tcp challenges. http challenges are served with https.

## Note

The plugin does not support different base path. API routes must be served strictly at the routes above.