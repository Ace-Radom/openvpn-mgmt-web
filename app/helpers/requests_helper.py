import requests


def build_url(host: str, port: int, endpoint: str, use_https: bool) -> str:
    if use_https:
        protocol = "https"
    else:
        protocol = "http"

    if port == -1:
        port_str = ""
    else:
        port_str = f":{ port }"

    if endpoint[0] == "/":
        endpoint = endpoint[1:]

    return f"{ protocol }://{ host }{ port_str }/{ endpoint }"


def get(
    host: str,
    port: int = -1,
    endpoint: str = "",
    use_https: bool = False,
    timeout: int = 5,
    crt_verify: bool = True,
) -> tuple[int, dict]:
    url = build_url(host, port, endpoint, use_https)
    try:
        response = requests.get(url, timeout=timeout, verify=crt_verify)
        return (response.status_code, response.json())
    except Exception as e:
        return (-1, {"msg": e})


def post(
    host: str,
    port: int = -1,
    endpoint: str = "",
    use_https: bool = False,
    timeout: int = 5,
    data: dict = {},
    crt_verify: bool = True,
) -> tuple[int, dict]:
    url = build_url(host, port, endpoint, use_https)
    try:
        response = requests.post(url, json=data, timeout=timeout, verify=crt_verify)
        return (response.status_code, response.json())
    except Exception as e:
        return (-1, {"msg": e})
