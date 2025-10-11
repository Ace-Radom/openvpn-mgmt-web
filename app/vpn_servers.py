from app import config
from app.helpers import redis_helper, requests_helper


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

    def check_alive(self) -> bool:
        status_code, _ = self._get("/alive")
        return status_code == 200


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
