import re
from flask import (
    Blueprint,
    session,
    jsonify,
    request,
)

from app import db, profiles, utils, vpn_servers
from app.email import gmail

bp = Blueprint("api", __name__)


@bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    code = data.get("invitation_code")
    password = data.get("password")
    email = data.get("email")
    if not code or not password or not email:
        return (
            jsonify(
                {
                    "success": False,
                    "msg": "Invitation code, password and email are required",
                }
            ),
            400,
        )
    if not db.invitation_code_exists(code):
        return jsonify({"success": False, "msg": "Invitation code doesn't exist"}), 400
    username = db.get_username_with_invitation_code(code)
    verify_token = db.add_user_not_verified(username, password, email)
    if verify_token is None:
        return jsonify({"success": False, "msg": "DB error"}), 500

    try:
        gmail.send_email(
            email,
            "验证您的邮箱 - OpenVPN Mgmt",
            "verify_zhCN.html",
            {
                "username": username,
                "verify_url": utils.build_server_link(
                    f"verify/user/{ verify_token }", is_public_link=True
                ),
            },
        )
    except:
        return jsonify({"success": False, "msg": "Failed to send verify email"}), 500

    db.pop_invitation_code(code)

    session["allow_success"] = True
    return jsonify({"success": True, "msg": "Registration successful"})


@bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"success": False, "msg": "Username and password required"}), 400
    if not db.check_user_password(username, password):
        return jsonify({"success": False, "msg": "Username or password incorrect"}), 401
    session["username"] = username
    session["allow_success"] = True
    return jsonify({"success": True, "msg": "Login successful"})


@bp.route("/api/invite", methods=["POST"])
def api_invite():
    if not session["username"]:
        return jsonify({"success": False, "msg": "User unauthorized"}), 401
    elif session["username"] != "Admin":
        return (
            jsonify(
                {
                    "success": False,
                    "msg": "Only admin is allowed to access this endpoint",
                }
            ),
            403,
        )

    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"success": False, "msg": "Username required"}), 400
    if not re.match(r"^[A-Z][a-z]*$", username):
        return jsonify({"success": False, "msg": "Illegal username"}), 400
    code = db.generate_invitation_code(username)
    if code is None:
        return jsonify({"success": False, "msg": "DB error"}), 500
    return jsonify({"success": True, "code": code})


@bp.route("/api/reqprofile", methods=["POST"])
def api_reqprofile():
    username = session["username"]

    if not username:
        return jsonify({"success": False, "msg": "User unauthorized"}), 401
    elif username == "Admin":
        return (
            jsonify(
                {
                    "success": False,
                    "msg": "Admin is not allowed to access this endpoint",
                }
            ),
            403,
        )

    data = request.json
    server_cn = data.get("server_common_name")
    profile_num = data.get("num")
    if not server_cn or not profile_num:
        return (
            jsonify(
                {"success": False, "msg": "Server common_name and profile num required"}
            ),
            400,
        )
    if not vpn_servers.exists(server_cn):
        return (
            jsonify(
                {"success": False, "msg": "Server common_name given doesn't exist"}
            ),
            400,
        )

    new_cns = profiles.request_profiles(server_cn, username, profile_num)
    if new_cns is None:
        return jsonify({"success": False, "msg": "Failed to request profiles"}), 500
    elif len(new_cns) == 0:
        return jsonify({"success": False, "msg": "Too many profiles"}), 403

    return jsonify({"success": True, "common_names": new_cns})


@bp.route("/api/list/invites")
def api_list_invites():
    if not session["username"]:
        return jsonify({"success": False, "msg": "User unauthorized"}), 401
    elif session["username"] != "Admin":
        return (
            jsonify(
                {
                    "success": False,
                    "msg": "Only admin is allowed to access this endpoint",
                }
            ),
            403,
        )

    codes = db.list_invitation_code()
    return jsonify({"success": True, "codes": codes})


@bp.route("/api/list/servers")
def api_list_servers():
    return jsonify({"success": True, "common_names": vpn_servers.list_servers()})


@bp.route("/api/list/profiles")
def api_list_profiles():
    username = session["username"]

    if not username:
        return jsonify({"success": False, "msg": "User unauthorized"}), 401
    elif username == "Admin":
        return (
            jsonify(
                {
                    "success": False,
                    "msg": "Admin is not allowed to access this endpoint",
                }
            ),
            403,
        )

    server_cns = vpn_servers.list_servers()
    common_names = {}
    for server_cn in server_cns:
        cns = profiles.list_user_profile_common_names(server_cn, username)
        if cns is None:
            continue
            return (
                jsonify(
                    {"success": False, "msg": "Failed to get profile common names"}
                ),
                500,
            )
        common_names[server_cn] = cns

    return jsonify({"success": True, "common_names": common_names})


@bp.route("/api/list/profilereqs")
def api_list_profilereqs():
    username = session["username"]

    if not username:
        return jsonify({"success": False, "msg": "User unauthorized"}), 401
    elif username == "Admin":
        requests_data = db.list_all_profile_requests()
    else:
        requests_data = db.list_user_profile_requests(username)

    if requests_data is None:
        return jsonify({"success": False, "msg": "DB error"}), 500
    # this should never happen: if username is not found in users table, sth is wrong with the db

    requests = [
        {
            k: data[k]
            for k in [
                "server_common_name",
                "common_name",
                "request_time_ts",
                "is_rejected",
            ]
            if k in data.keys()
        }
        for data in requests_data
    ]
    return jsonify({"success": True, "requests": requests})


@bp.route("/api/operate/profilereq", methods=["POST"])
def api_operate_profilereq():
    if not session["username"]:
        return jsonify({"success": False, "msg": "User unauthorized"}), 401
    elif session["username"] != "Admin":
        return (
            jsonify(
                {
                    "success": False,
                    "msg": "Only admin is allowed to access this endpoint",
                }
            ),
            403,
        )
    
    data = request.json
    server_cn = data.get("server_common_name")
    cn = data.get("common_name")
    op = data.get("operation")
    if not server_cn or not cn or not op:
        return jsonify({"success": False, "msg": "Server Common_name, common_name and operation required"}), 400
    if op not in ["approve", "reject"]:
        return jsonify({"success": False, "msg": "Illegal operation"}), 400
    if not vpn_servers.exists(server_cn):
        return (
            jsonify(
                {"success": False, "msg": "Server common_name given doesn't exist"}
            ),
            400,
        )
    if not db.profile_request_exists(server_cn, cn):
        return jsonify({"success": False, "msg": "Profile request doesn't exist"}), 400
    
    if op == "approve":
        if not profiles.approve_profile_request(server_cn, cn):
            return jsonify({"success": False, "msg": "Failed to confirm profile request"}), 500
    elif op == "reject":
        if not profiles.reject_profile_request(server_cn, cn):
            return jsonify({"success": False, "msg": "Failed to reject profile request"}), 500

    return jsonify({"success": True})    
    