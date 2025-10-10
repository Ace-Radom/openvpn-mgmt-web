import redis
from typing import Optional, Union

from app import config

_global_redis_obj = None

def init() -> None:
    global _global_redis_obj

    _global_redis_obj = redis.from_url(config.config["redis"]["db_url"])

def get(key: str) -> str | None:
    global _global_redis_obj

    try:
        return _global_redis_obj.get(key).decode()
    except:
        return None
    
def set(key: str, value: Union[str, int, float], ex: Optional[int] = None) -> bool:
    global _global_redis_obj

    try:
        return _global_redis_obj.set(key, value, ex=ex)
    except:
        return False
