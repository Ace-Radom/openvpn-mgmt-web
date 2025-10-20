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
    crt_path: str = None,
) -> tuple[int, dict]:
    url = build_url(host, port, endpoint, use_https)
    if crt_verify:
        verify = crt_path
    else:
        verify = False

    try:
        response = requests.get(url, timeout=timeout, verify=verify)
        return (response.status_code, response.json())
    except Exception as e:
        return (-1, {"msg": e})


def post(
    host: str,
    port: int = -1,
    endpoint: str = "",
    use_https: bool = False,
    timeout: int = 5,
    auth=None,
    data: dict = {},
    crt_verify: bool = True,
    crt_path: str = None,
    requests_send_with_data_param: bool = False,
) -> tuple[int, dict]:
    url = build_url(host, port, endpoint, use_https)
    if crt_verify:
        verify = crt_path
    else:
        verify = False

    try:
        if requests_send_with_data_param:
            response = requests.post(
                url, auth=auth, data=data, timeout=timeout, verify=verify
            )
        else:
            response = requests.post(
                url, auth=auth, json=data, timeout=timeout, verify=verify
            )
        return (response.status_code, response.json())
    except Exception as e:
        return (-1, {"msg": e})


def download(
    host: str,
    port: int = -1,
    endpoint: str = "",
    use_https: bool = False,
    timeout: int = 5,
    crt_verify: bool = True,
    crt_path: str = None,
    download_to: str = "",
) -> tuple[int, dict]:
    url = build_url(host, port, endpoint, use_https)
    if crt_verify:
        verify = crt_path
    else:
        verify = False

    try:
        with requests.get(url, stream=True, timeout=timeout, verify=verify) as response:
            if response.status_code == 200:
                with open(download_to, "wb") as file:
                    for chunk in response.iter_content(chunk_size=4096):
                        if chunk:
                            file.write(chunk)
                return (200, {})
            else:
                return (response.status_code, response.json())
    except Exception as e:
        return (-1, {"msg": e})
