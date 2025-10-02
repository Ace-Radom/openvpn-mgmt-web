import ipaddress
import random
import string

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
