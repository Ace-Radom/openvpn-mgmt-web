import os
import redis
import urllib3

from flask_session import Session as ServerSideSession

from app import config, create_app, db, profiles, vpn_servers, utils
from app.email import gmail
from app.helpers import redis_helper

base_dir = os.path.split(os.path.realpath(__file__))[0]
config.parse_config(os.path.join(base_dir, "web.cfg"))
if config.config["app"]["secret_key"] is None:
    raise RuntimeError("Secret key cannot be None")

utils.create_temp_dir_if_not_exists()

app = create_app()
app.secret_key = config.config["app"]["secret_key"]
app.config.from_object("app.flask_config")
if config.config["app"]["is_production_env"]:
    app.config.update(DEBUG=False, SESSION_COOKIE_SECURE=True)
else:
    app.config.update(DEBUG=True)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app.config.update(
    SESSION_TYPE="redis",
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_KEY_PREFIX=config.config["redis"]["session_key_prefix"],
    SESSION_REDIS=redis.from_url(config.config["redis"]["db_url"]),
)
ServerSideSession(app)

if not db.init_db():
    raise RuntimeError("Init DB failed")

gmail.fetch_gmail_discovery()
gmail.auth_gmail_api()
gmail.secure_gmail_related_files()

redis_helper.init()
vpn_servers.init()

for server in vpn_servers.list_servers():
    profiles.sync_profile_cache(server)

if not db.admin_exists():
    if not db.add_admin():
        raise RuntimeError("Add admin failed")

if __name__ == "__main__":
    app.run()
