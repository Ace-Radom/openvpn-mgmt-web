from flask import Blueprint, session, jsonify, make_response, send_file

from app import profiles, vpn_servers

bp = Blueprint("download", __name__)


@bp.route("/download/profiles/<server_cn>/<common_name>")
def download_profiles(server_cn, common_name):
    username = session["username"]

    if not username:
        return jsonify({"success": False, "msg": "User unauthorized"}), 401
    elif not common_name.startswith(username):
        return (
            jsonify(
                {
                    "success": False,
                    "msg": "Downloading profiles from other users is not allowed",
                }
            ),
            403,
        )
    elif not vpn_servers.exists(server_cn):
        return (
            jsonify(
                {"success": False, "msg": "Server common_name given doesn't exist"}
            ),
            400,
        )
    elif not profiles.check_cn_exists(server_cn, common_name):
        return (
            jsonify({"success": False, "msg": "Profile common_name doesn't exist"}),
            404,
        )

    profile_path = profiles.get_profile_path(server_cn, common_name)
    if profile_path is None:
        return jsonify({"success": False, "msg": "Failed to prepare profile file"}), 500

    response = make_response(
        send_file(
            profile_path,
            as_attachment=True,
            download_name=f"{ common_name }.ovpn",
            mimetype="application/x-openvpn-profile",
        )
    )
    response.headers["X-Profile-Common-Name"] = common_name

    return response
