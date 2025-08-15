from __future__ import annotations
from typing import Any
from passlib.context import CryptContext
from itsdangerous import URLSafeSerializer, BadSignature
from cryptography.fernet import Fernet


class PasswordHasher:
    def __init__(self) -> None:
        self._ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, raw_password: str) -> str:
        return self._ctx.hash(raw_password)

    def verify(self, raw_password: str, hashed_password: str) -> bool:
        return self._ctx.verify(raw_password, hashed_password)


class CookieSigner:
    def __init__(self, secret_key: str) -> None:
        self._signer = URLSafeSerializer(secret_key)

    def dumps(self, data: dict[str, Any]) -> str:
        return self._signer.dumps(data)

    def loads(self, token: str) -> dict[str, Any] | None:
        try:
            return self._signer.loads(token)
        except BadSignature:
            return None


class SecretBox:
    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key.encode())

    def encrypt(self, data: str) -> str:
        return self._fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        return self._fernet.decrypt(token.encode()).decode()
