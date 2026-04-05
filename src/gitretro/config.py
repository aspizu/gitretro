from pathlib import Path

import msgspec.toml

_config_path = Path("~/.config/gitretro/config.toml").expanduser()


class Account(msgspec.Struct):
    email: str
    api_key: str


class Config(msgspec.Struct):
    accounts: list[Account]

    @staticmethod
    def load() -> Config:
        data = _config_path.read_bytes()
        return msgspec.toml.decode(data, type=Config)


config = Config.load()
