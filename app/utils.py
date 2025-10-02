import ipaddress

from app import config

ZZDS_SCHOOL_WLAN_IP = ipaddress.ip_network("31.22.24.219")


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

    if remote in ZZDS_SCHOOL_WLAN_IP:
        return True
