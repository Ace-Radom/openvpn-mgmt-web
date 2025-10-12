import hashlib
import json
import os
import shutil

from app import config, utils
from app import vpn_servers as servers
from app.helpers import redis_helper
from app.vpn_servers import vpn_servers


def get_profile_index(server_cn: str) -> dict | None:
    index = None

    if vpn_servers[server_cn].check_profile_cache_enabled():
        prefix = config.config["redis"]["profile_key_prefix"]
        key = f"{ prefix }{ server_cn }:index_cache"
        index_str = redis_helper.get(key)
        try:
            index = json.loads(index_str)
        except:
            index = None

    if index is None:
        index = vpn_servers[server_cn].get_profile_index()

    return index


def get_profile_cache_dir(server_cn: str) -> str:
    return os.path.join(config.config["app"]["profiles_cache_dir"], server_cn)


def cache_index(server_cn: str, index: str) -> bool:
    prefix = config.config["redis"]["profile_key_prefix"]
    key = f"{ prefix }{ server_cn }:index_cache"
    return redis_helper.set(key, json.dumps(index))


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
