from app import config
from app.helpers import requests_helper


class vpn_server:
    def __init__(
        self,
        ip: str,
        port: int,
        use_https: bool,
        enable_usage: bool,
        usage_refresh_interval: int,
        enable_profile_cache: bool,
        profile_cache_refresh_interval: int,
        profile_cache_expire_after: int,
        enable_crt_verify: bool,
    ) -> None:
        self._ip = ip
        self._port = port
        self._use_https = use_https
        self._enable_usage = enable_usage
        self._usage_refresh_interval = usage_refresh_interval
        self._enable_profile_cache = enable_profile_cache
        self._profile_cache_refresh_interval = profile_cache_refresh_interval
        self._profile_cache_expire_after = profile_cache_expire_after
        self._enable_crt_verify = enable_crt_verify
        return

    def _get(self, endpoint: str) -> tuple[int, dict]:
        return requests_helper.get(
            self._ip,
            port=self._port,
            endpoint=endpoint,
            use_https=self._use_https,
            crt_verify=self._enable_crt_verify,
        )

    def _post(self, endpoint: str, data: dict) -> tuple[int, dict]:
        return requests_helper.post(
            self._ip,
            port=self._port,
            endpoint=endpoint,
            use_https=self._use_https,
            data=data,
            crt_verify=self._enable_crt_verify,
        )

    def _download(self, endpoint: str, download_to: str) -> tuple[int, dict]:
        return requests_helper.download(
            self._ip,
            port=self._port,
            endpoint=endpoint,
            use_https=self._use_https,
            crt_verify=self._enable_crt_verify,
            download_to=download_to,
        )

    def check_alive(self) -> bool:
        status_code, _ = self._get("/alive")
        return status_code == 200

    def get_profile_index(self) -> dict | None:
        status_code, data = self._get("/profiles/index")
        if status_code != 200:
            return None

        return data["data"]

    def get_max_profiles_per_user(self) -> int | None:
        status_code, data = self._get("/profiles/maxperusr")
        if status_code != 200:
            return None

        return data["data"]["max_per_user"]

    def check_profile_exists(self, common_name: str) -> bool | None:
        status_code, data = self._post("/profiles/exist", {"common_name": common_name})
        if status_code != 200:
            return None

        return data["data"]["exist"]

    def add_profile(self, username: str, common_name: str) -> bool:
        status_code, _ = self._post(
            "/profiles/add", {"username": username, "common_name": common_name}
        )
        return status_code == 200

    def download_profile(self, common_name: str, download_to: str) -> bool:
        status_code, _ = self._download(
            f"/profiles/download/{ common_name }", download_to
        )
        return status_code == 200

    # TODO: download hash check

    def check_profile_cache_enabled(self) -> bool:
        return self._enable_profile_cache

    def get_profile_cache_expire_after(self) -> int:
        return self._profile_cache_expire_after


vpn_servers: dict[str, vpn_server] = {}


def init():
    cns = config.config["vpn_server"]["server_cn"]
    for cn in cns:
        vpn_servers[cn] = vpn_server(
            config.config["vpn_server_data"][cn]["ip"],
            config.config["vpn_server_data"][cn]["port"],
            config.config["vpn_server_data"][cn]["use_https"],
            config.config["vpn_server_data"][cn]["enable_usage"],
            config.config["vpn_server_data"][cn]["usage_refresh_interval"],
            config.config["vpn_server_data"][cn]["enable_profile_cache"],
            config.config["vpn_server_data"][cn]["profile_cache_refresh_interval"],
            config.config["vpn_server_data"][cn]["profile_cache_expire_after"],
            config.config["vpn_server_data"][cn]["enable_crt_verify"],
        )


def exists(server_cn: str):
    return server_cn in vpn_servers.keys()


def list_servers() -> list:
    return list(vpn_servers.keys())
