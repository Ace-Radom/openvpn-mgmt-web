import hashlib
import json
import os
import re
import shutil

from app import config, utils
from app import vpn_servers as servers
from app.helpers import redis_helper
from app.vpn_servers import vpn_servers


def get_cache_key(server_cn: str, cache_name: str) -> str:
    prefix = config.config["redis"]["profile_key_prefix"]
    key = f"{ prefix }{ server_cn }:{ cache_name }"
    return key


def get_profile_cache_dir(server_cn: str) -> str:
    return os.path.join(config.config["app"]["profiles_cache_dir"], server_cn)


def cache_index(server_cn: str, index: str) -> bool:
    key = get_cache_key(server_cn, "index_cache")
    return redis_helper.set(
        key,
        json.dumps(index),
        ex=vpn_servers[server_cn].get_profile_cache_expire_after(),
    )


def cache_max_profiles_per_user(server_cn: str, num: int) -> bool:
    key = get_cache_key(server_cn, "max_profile_per_user_cache")
    return redis_helper.set(
        key, num, ex=vpn_servers[server_cn].get_profile_cache_expire_after()
    )


def sync_profile_cache(server_cn: str) -> bool:
    if not servers.exists(server_cn):
        return False

    if not vpn_servers[server_cn].check_profile_cache_enabled():
        return True
    # profile cache disabled, no need to let caller know since it won't break anything

    cache_dir = get_profile_cache_dir(server_cn)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    if not os.path.isdir(cache_dir):
        return False

    index = vpn_servers[server_cn].get_profile_index()
    if index is None:
        return False
    # get index from remote failed
    if not cache_index(server_cn, index):
        return False

    max_profiles_per_user = vpn_servers[server_cn].get_max_profiles_per_user()
    if max_profiles_per_user is None:
        return False
    if not cache_max_profiles_per_user(server_cn, max_profiles_per_user):
        return False

    # TODO: ensure sync process atomicity

    hash_func = index["hash"]
    profiles_data = index["profiles"]
    need_to_update_filenames = []

    for data in profiles_data:
        filename = data["filename"]
        hash = data["hash"]
        profile_cache_path = os.path.join(cache_dir, filename)
        if os.path.exists(profile_cache_path):
            hasher = hashlib.new(hash_func)
            with open(profile_cache_path, "rb") as file:
                for chunk in iter(lambda: file.read(1024), b""):
                    hasher.update(chunk)
            if hasher.hexdigest().lower() == hash.lower():
                continue
            # same file, no need to download again

        need_to_update_filenames.append(filename)
        # cached file doesn't exist or changed, need to cache again

    for filename in need_to_update_filenames:
        temp_path = utils.gen_temp_path()
        cn = os.path.splitext(filename)[0]

        if vpn_servers[server_cn].download_profile(cn, temp_path):
            profile_cache_path = os.path.join(cache_dir, filename)
            shutil.copyfile(temp_path, profile_cache_path)
            # old file will be overwritten

        if os.path.exists(temp_path):
            os.remove(temp_path)
        # remove temp file
    # TODO: ensure sync process atomicity

    return True


def get_profile_index(server_cn: str) -> dict | None:
    index = None

    if vpn_servers[server_cn].check_profile_cache_enabled():
        key = get_cache_key(server_cn, "index_cache")
        index_str = redis_helper.get(key)
        try:
            index = json.loads(index_str)
        except:
            index = None

    if index is None:
        index = vpn_servers[server_cn].get_profile_index()

    return index


def get_max_profiles_per_user(server_cn: str) -> int | None:
    num = None

    if vpn_servers[server_cn].check_profile_cache_enabled():
        key = get_cache_key(server_cn, "max_profile_per_user_cache")
        num_str = redis_helper.get(key)
        try:
            num = int(num_str)
        except:
            num = None

    if num is None:
        num = vpn_servers[server_cn].get_max_profiles_per_user()

    return num


def check_cn_exists(server_cn: str, common_name: str) -> bool | None:
    """
    check common name existance (from profile index)
    """
    index = get_profile_index(server_cn)
    if index is None:
        return None

    return any(
        data["filename"] == f"{ common_name }.ovpn" for data in index["profiles"]
    )


def check_profile_exists(server_cn: str, common_name: str) -> bool | None:
    """
    check profile existance (with the lowest-level method)

    if a profile is added by `openvpn-install.sh` but doesn't exist in index file,
    it will still return true

    therefore: this function cannot replace `check_cn_exists()`, cuz it only checks
    if the common name exists in (cached) index
    """
    if not servers.exists(server_cn):
        return False

    return vpn_servers[server_cn].check_profile_exists(common_name)


def request_profiles(server_cn: str, username: str, num: int) -> list | None:
    """
    request some profiles

    if allowed, return a list of new profiles' cn;
    if more profiles than `max_profiles_per_user` are requested, returns `None`

    this is not same as add_profile(): it only request names, waiting for admin to confirm
    """
    if not servers.exists(server_cn):
        return None

    index = get_profile_index(server_cn)
    max_profiles_per_user = get_max_profiles_per_user(server_cn)
    if index is None or max_profiles_per_user is None:
        return None

    profile_filenames = [data["filename"] for data in index["profiles"]]
    user_profile_filenames = [
        filename for filename in profile_filenames if filename.startswith(username)
    ]

    if len(user_profile_filenames) + num > max_profiles_per_user:
        return None
    # more profiles than max_profiles_per_user, deny

    max_profile_index = -1
    for filename in user_profile_filenames:
        try:
            pattern = re.compile(rf"^{ username }-(\d+)\.ovpn$")
            match = pattern.match(filename)
            if match:
                profile_index = int(match.group(1))
                max_profile_index = max(profile_index, max_profile_index)
        except:
            pass
        # should actually never happen

    new_cns = []
    for i in range(max_profile_index + 1, max_profile_index + 1 + num):
        new_cns.append(f"{ username }-{ i }")

    return new_cns
