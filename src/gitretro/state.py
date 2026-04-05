import json
import time
from pathlib import Path

_state_path = Path("~/.config/gitretro/state.json").expanduser()


def _load() -> dict[str, float]:
    try:
        return json.loads(_state_path.read_text())
    except FileNotFoundError:
        return {}


def _save(state: dict[str, float]) -> None:
    _state_path.parent.mkdir(parents=True, exist_ok=True)
    _state_path.write_text(json.dumps(state))


def get_expiry(email: str) -> float:
    return _load().get(email, 0.0)


def set_expiry(email: str, delay: int) -> None:
    state = _load()
    state[email] = time.time() + delay
    _save(state)
