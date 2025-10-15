import configparser
import ipaddress

from app.utils import is_valid_ipv4

config = {
    "app": {
        "secret_key": None,
        "is_production_env": False,
        "db_path": "/var/openvpn-mgmt/web/users.db",
        "profiles_cache_dir": "/var/openvpn-mgmt/web/cached_profiles/",
        "temp_dir": "/tmp/openvpn-mgmt/web/",
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
    "vpn_server": {"server_cn": []},  # common names
    "vpn_server_data": {},  # cn as key
    "redis": {
        "profile_key_prefix": "openvpn-mgmt-web-profile:",
        "session_key_prefix": "openvpn-mgmt-web-session:",
        "db_url": "redis://127.0.0.1:6379",
    },
    "gmail": {
        "discovery_path": "/var/openvpn-mgmt/web/gmail/gmail_v1_discovery.json",
        "token_path": "/var/openvpn-mgmt/web/gmail/token.json",
        "secret_path": "/var/openvpn-mgmt/web/gmail/secret.json",
        "sender_email_addr": None,
        "app_pswd": None,
    },
    "mailgun": {
        "api_host": "api.mailgun.net",
        "api_endpoint": None,
        "api_key": None,
        "sender_name": None,
        "sender_email_addr": None,
        "bcc_email_addr": []
    }
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
        if (
            parser.has_option("app", "profiles_cache_dir")
            and len(parser["app"]["profiles_cache_dir"]) != 0
        ):
            config["app"]["profiles_cache_dir"] = parser["app"]["profiles_cache_dir"]
        if parser.has_option("app", "temp_dir") and len(parser["app"]["temp_dir"]) != 0:
            config["app"]["temp_dir"] = parser["app"]["temp_dir"]

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

    if parser.has_section("vpn_server"):
        if (
            parser.has_option("vpn_server", "server_cn")
            and len(parser["vpn_server"]["server_cn"]) != 0
        ):
            if parser["vpn_server"]["server_cn"].find(",") == -1:
                config["vpn_server"]["server_cn"] = [parser["vpn_server"]["server_cn"]]
            else:
                cns = parser["vpn_server"]["server_cn"].split(",")
                for cn in cns:
                    config["vpn_server"]["server_cn"].append(cn.strip())

    for cn in config["vpn_server"]["server_cn"]:
        section_name = f"vpn_server:{ cn }"
        if parser.has_section(section_name):
            config["vpn_server_data"][cn] = {}
            if (
                parser.has_option(section_name, "ip")
                and len(parser[section_name]["ip"]) != 0
                and is_valid_ipv4(parser[section_name]["ip"])
            ):
                config["vpn_server_data"][cn]["ip"] = parser[section_name]["ip"]
            if (
                parser.has_option(section_name, "port")
                and len(parser[section_name]["port"]) != 0
                and parser[section_name]["port"].isdigit()
            ):
                config["vpn_server_data"][cn]["port"] = int(
                    parser[section_name]["port"]
                )
            if (
                parser.has_option(section_name, "use_https")
                and len(parser[section_name]["use_https"]) != 0
                and parser[section_name]["use_https"].isdigit()
            ):
                config["vpn_server_data"][cn]["use_https"] = (
                    int(parser[section_name]["use_https"]) != 0
                )
            if (
                parser.has_option(section_name, "enable_usage")
                and len(parser[section_name]["enable_usage"]) != 0
                and parser[section_name]["enable_usage"].isdigit()
            ):
                config["vpn_server_data"][cn]["enable_usage"] = (
                    int(parser[section_name]["enable_usage"]) != 0
                )
            if (
                parser.has_option(section_name, "usage_refresh_interval")
                and len(parser[section_name]["usage_refresh_interval"]) != 0
                and parser[section_name]["usage_refresh_interval"].isdigit()
            ):
                config["vpn_server_data"][cn]["usage_refresh_interval"] = int(
                    parser[section_name]["usage_refresh_interval"]
                )
            if (
                parser.has_option(section_name, "enable_profile_cache")
                and len(parser[section_name]["enable_profile_cache"])
                and parser[section_name]["enable_profile_cache"].isdigit()
            ):
                config["vpn_server_data"][cn]["enable_profile_cache"] = (
                    int(parser[section_name]["enable_profile_cache"]) != 0
                )
            if (
                parser.has_option(section_name, "profile_cache_refresh_interval")
                and len(parser[section_name]["profile_cache_refresh_interval"]) != 0
                and parser[section_name]["profile_cache_refresh_interval"].isdigit()
            ):
                config["vpn_server_data"][cn]["profile_cache_refresh_interval"] = int(
                    parser[section_name]["profile_cache_refresh_interval"]
                )
            if (
                parser.has_option(section_name, "profile_cache_expire_after")
                and len(parser[section_name]["profile_cache_expire_after"])
                and parser[section_name]["profile_cache_expire_after"].isdigit()
            ):
                config["vpn_server_data"][cn]["profile_cache_expire_after"] = int(
                    parser[section_name]["profile_cache_expire_after"]
                )
            if (
                parser.has_option(section_name, "enable_crt_verify")
                and len(parser[section_name]["enable_crt_verify"])
                and parser[section_name]["enable_crt_verify"].isdigit()
            ):
                config["vpn_server_data"][cn]["enable_crt_verify"] = (
                    int(parser[section_name]["enable_crt_verify"]) != 0
                )

    if parser.has_section("redis"):
        if (
            parser.has_option("redis", "session_key_prefix")
            and len(parser["redis"]["session_key_prefix"]) != 0
        ):
            config["redis"]["session_key_prefix"] = parser["redis"][
                "session_key_prefix"
            ]
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
        if parser.has_option("gmail", "app_pswd") and len(parser["gmail"]["app_pswd"]) != 0:
            config["gmail"]["app_pswd"] = parser["gmail"]["app_pswd"]

    if parser.has_section("mailgun"):
        if parser.has_option("mailgun", "api_host") and len(parser["mailgun"]["api_host"]) != 0:
            config["mailgun"]["api_host"] = parser["mailgun"]["api_host"]
        if parser.has_option("mailgun", "api_endpoint") and len(parser["mailgun"]["api_endpoint"]) != 0:
            config["mailgun"]["api_endpoint"] = parser["mailgun"]["api_endpoint"]
        if parser.has_option("mailgun", "api_key") and len(parser["mailgun"]["api_key"]) != 0:
            config["mailgun"]["api_key"] = parser["mailgun"]["api_key"]
        if parser.has_option("mailgun", "sender_name") and len(parser["mailgun"]["sender_name"]) != 0:
            config["mailgun"]["sender_name"] = parser["mailgun"]["sender_name"]
        if parser.has_option("mailgun", "sender_email_addr") and len(parser["mailgun"]["sender_email_addr"]) != 0:
            config["mailgun"]["sender_email_addr"] = parser["mailgun"]["sender_email_addr"]
        if parser.has_option("mailgun", "bcc_email_addr") and len(parser["mailgun"]["bcc_email_addr"]) != 0:
            if parser["mailgun"]["bcc_email_addr"].find(",") == -1:
                config["mailgun"]["bcc_email_addr"] = [parser["mailgun"]["bcc_email_addr"]]
            else:
                addrs = parser["mailgun"]["bcc_email_addr"].split(",")
                for addr in addrs:
                    config["mailgun"]["bcc_email_addr"].append(addr.strip())
