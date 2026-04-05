import time

from google import genai

from . import state
from .config import Account, config

_clients: dict[str, genai.Client] = {}


def _client(account: Account) -> genai.Client:
    if account.email not in _clients:
        _clients[account.email] = genai.Client(api_key=account.api_key)
    return _clients[account.email]


def pick_with_wait() -> tuple[Account, genai.Client, float]:
    now = time.time()
    soonest_account = config.accounts[0]
    soonest_expiry = float("inf")
    for account in config.accounts:
        expiry = state.get_expiry(account.email)
        if expiry <= now:
            return account, _client(account), 0.0
        if expiry < soonest_expiry:
            soonest_expiry = expiry
            soonest_account = account
    return soonest_account, _client(soonest_account), soonest_expiry - now


def mark_rate_limited(email: str, delay: int) -> None:
    state.set_expiry(email, delay)
