import configparser
import ipaddress

from app.utils import is_valid_ipv4

config = {
    "app": {
        "secret_key": None,
        "is_production_env": False,
        "db_path": "/var/openvpn-mgmt/web/users.db",
    },
    "server": {
        "public_ip": None,
        "private_ip": None,
        "port": None,
        "domain_name": None,
        "use_https": False,
        # all traffics should be forwarded by nginx
        # so if nginx enables https, we need to know
        "use_domain_name": False,
    },
    "registration": {
        "zzds_school_wlan_ip": None,
        "allow_all_registration_request_under_production_env": False,
    },
    "redis": {
        "key_prefix": "openvpn-mgmt-web-session:",
        "db_url": "redis://127.0.0.1:6379",
    },
    "gmail": {
        "discovery_path": "/var/openvpn-mgmt/web/gmail/gmail_v1_discovery.json",
        "token_path": "/var/openvpn-mgmt/web/gmail/token.json",
        "secret_path": "/var/openvpn-mgmt/web/gmail/secret.json",
        "sender_email_addr": None,
    },
}


def parse_config(config_path: str):
    parser = configparser.ConfigParser()
    parser.read(config_path)

    if parser.has_section("app"):
        if (
            parser.has_option("app", "secret_key")
            and len(parser["app"]["secret_key"]) != 0
        ):
            config["app"]["secret_key"] = parser["app"]["secret_key"]
        if (
            parser.has_option("app", "is_production_env")
            and len(parser["app"]["is_production_env"]) != 0
            and parser["app"]["is_production_env"].isdigit()
        ):
            config["app"]["is_production_env"] = (
                int(parser["app"]["is_production_env"]) != 0
            )
        if parser.has_option("app", "db_path") and len(parser["app"]["db_path"]) != 0:
            config["app"]["db_path"] = parser["app"]["db_path"]

    if parser.has_section("server"):
        if (
            parser.has_option("server", "public_ip")
            and len(parser["server"]["public_ip"]) != 0
            and is_valid_ipv4(parser["server"]["public_ip"])
        ):
            config["server"]["public_ip"] = parser["server"]["public_ip"]
        if (
            parser.has_option("server", "private_ip")
            and len(parser["server"]["private_ip"]) != 0
            and is_valid_ipv4(parser["server"]["private_ip"])
        ):
            config["server"]["private_ip"] = parser["server"]["private_ip"]
        if (
            parser.has_option("server", "port")
            and len(parser["server"]["port"]) != 0
            and parser["server"]["port"].isdigit()
        ):
            config["server"]["port"] = int(parser["server"]["port"])
        if (
            parser.has_option("server", "domain_name")
            and len(parser["server"]["domain_name"]) != 0
        ):
            config["server"]["domain_name"] = parser["server"]["domain_name"]
        if (
            parser.has_option("server", "use_https")
            and len(parser["server"]["use_https"]) != 0
            and parser["server"]["use_https"].isdigit()
        ):
            config["server"]["use_https"] = int(parser["server"]["use_https"]) != 0
        if (
            parser.has_option("server", "use_domain_name")
            and len(parser["server"]["use_domain_name"]) != 0
            and parser["server"]["use_domain_name"].isdigit()
            and config["server"]["domain_name"] is not None
        ):
            config["server"]["use_domain_name"] = (
                int(parser["server"]["use_domain_name"]) != 0
            )

    if parser.has_section("registration"):
        if (
            parser.has_option("registration", "zzds_school_wlan_ip")
            and len(parser["registration"]["zzds_school_wlan_ip"]) != 0
            and is_valid_ipv4(parser["registration"]["zzds_school_wlan_ip"])
        ):
            config["registration"]["zzds_school_wlan_ip"] = ipaddress.ip_address(
                parser["registration"]["zzds_school_wlan_ip"]
            )
        # build IPv4Address object here to avoid multi-construction
        if (
            parser.has_option(
                "registration", "allow_all_registration_request_under_production_env"
            )
            and len(
                parser["registration"][
                    "allow_all_registration_request_under_production_env"
                ]
            )
            != 0
            and parser["registration"][
                "allow_all_registration_request_under_production_env"
            ].isdigit()
        ):
            config["registration"][
                "allow_all_registration_request_under_production_env"
            ] = (
                int(
                    parser["registration"][
                        "allow_all_registration_request_under_production_env"
                    ]
                )
                != 0
            )

    if parser.has_section("redis"):
        if (
            parser.has_option("redis", "key_prefix")
            and len(parser["redis"]["key_prefix"]) != 0
        ):
            config["redis"]["key_prefix"] = parser["redis"]["key_prefix"]
        if parser.has_option("redis", "db_url") and len(parser["redis"]["db_url"]) != 0:
            config["redis"]["db_url"] = parser["redis"]["db_url"]

    if parser.has_section("gmail"):
        if (
            parser.has_option("gmail", "discovery_path")
            and len(parser["gmail"]["discovery_path"]) != 0
        ):
            config["gmail"]["discovery_path"] = parser["gmail"]["discovery_path"]
        if (
            parser.has_option("gmail", "token_path")
            and len(parser["gmail"]["token_path"]) != 0
        ):
            config["gmail"]["token_path"] = parser["gmail"]["token_path"]
        if (
            parser.has_option("gmail", "secret_path")
            and len(parser["gmail"]["secret_path"]) != 0
        ):
            config["gmail"]["secret_path"] = parser["gmail"]["secret_path"]
        if (
            parser.has_option("gmail", "sender_email_addr")
            and len(parser["gmail"]["sender_email_addr"]) != 0
            and parser["gmail"]["sender_email_addr"].find("@gmail.com") != -1
        ):
            config["gmail"]["sender_email_addr"] = parser["gmail"]["sender_email_addr"]
