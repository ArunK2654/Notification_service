import json

from redis import Redis


class RedisService:
    def __init__(self, client: Redis):
        self.client = client

    def get(self, key: str) -> bytes | str | None:
        return self.client.get(key)

    def set(self, key: str, value: str, expire_seconds: int | None = None) -> None:
        self.client.set(key, value, ex=expire_seconds)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def ping(self) -> bool:
        return bool(self.client.ping())

    def set_json(
        self,
        key: str,
        value: object,
        expire_seconds: int | None = None,
    ) -> None:
        serialized_value = json.dumps(value)
        self.set(key=key, value=serialized_value, expire_seconds=expire_seconds)

    def get_json(self, key: str) -> object | None:
        value = self.get(key)
        if value is None:
            return None
        else:
            return json.loads(value)
