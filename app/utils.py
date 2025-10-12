import ipaddress
import os
import random
import string
import uuid

from app import config

RANDOM_CHARSET = string.ascii_letters + string.digits


def build_server_link(route: str, is_public_link: bool = False) -> str:
    if config.config["server"]["use_domain_name"]:
        host = config.config["server"]["domain_name"]
    else:
        if is_public_link:
            host_ip = config.config["server"]["public_ip"]
            host_port = config.config["server"]["port"]
        else:
            host_ip = config.config["server"]["private_ip"]
            host_port = config.config["server"]["port"]
        host = f"{ host_ip }:{ host_port }"

    if config.config["server"]["use_https"]:
        protocol = "https"
    else:
        protocol = "http"

    if route[0] == "/":
        route = route[1:]

    return f"{ protocol }://{ host }/{ route }"


def is_valid_ipv4(ip: str) -> bool:
    try:
        _ = ipaddress.IPv4Address(ip)
        return True
    except:
        return False


def is_request_from_zzds_school_wlan(remote_ip: str) -> bool:
    if not remote_ip:
        return False

    try:
        remote = ipaddress.ip_address(remote_ip)
    except:
        return False

    if remote == config.config["registration"]["zzds_school_wlan_ip"]:
        return True


def generate_random_str(length: int) -> str:
    return "".join(random.choice(RANDOM_CHARSET) for _ in range(length))


def create_temp_dir_if_not_exists() -> None:
    temp_dir = config.config["app"]["temp_dir"]
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    if not os.path.isdir(temp_dir):
        raise RuntimeError("Temp dir is not a directory")
    # no fkn idea why this would happen...
    # but anyway


def gen_temp_path() -> str:
    create_temp_dir_if_not_exists()

    temp_dir = config.config["app"]["temp_dir"]
    temp_path = os.path.join(temp_dir, f"{ uuid.uuid4().hex }.tmp")
    while os.path.exists(temp_path):
        temp_path = os.path.join(temp_dir, f"{ uuid.uuid4().hex }.tmp")

    return temp_path
