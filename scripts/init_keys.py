import os
from pathlib import Path
from secrets import token_urlsafe
from cryptography.fernet import Fernet


def parse_env(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            result[k.strip()] = v.strip()
    return result


def build_env(existing: dict[str, str]) -> str:
    lines = []
    keys_order = [
        "DATABASE_URL",
        "TELEGRAM_BOT_TOKEN",
        "SECRET_KEY",
        "FERNET_KEY",
        "ADMIN_USERNAME",
        "ADMIN_PASSWORD",
        "APP_HOST",
        "APP_PORT",
    ]
    for k in keys_order:
        if k in existing:
            lines.append(f"{k}={existing[k]}")
    for k, v in existing.items():
        if k not in keys_order:
            lines.append(f"{k}={v}")
    return "\n".join(lines) + "\n"


def main() -> None:
    env_path = Path(".env")
    env_text = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    env = parse_env(env_text)
    changed = False
    if not env.get("SECRET_KEY"):
        env["SECRET_KEY"] = token_urlsafe(48)
        changed = True
    if not env.get("FERNET_KEY"):
        env["FERNET_KEY"] = Fernet.generate_key().decode()
        changed = True
    if changed:
        env_path.write_text(build_env(env), encoding="utf-8")


if __name__ == "__main__":
    main()

