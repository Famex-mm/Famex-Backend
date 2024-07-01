import requests

from rest_api.models import MarketMakingPool
from website_backend.constants import TRADING_API_NETWORK_NAMES
from website_backend.settings import TRADING_API_USERNAME, TRADING_API_PASSWORD, TRADING_API_URL


def system_connect():
    body = {
        "username": TRADING_API_USERNAME,
        "password": TRADING_API_PASSWORD,
        "scope": "system"
    }

    response = requests.post(
        f"{TRADING_API_URL}/api/avatea/token", data=body
    )

    return response.json()["access_token"]


def update_algo_creation(instance: MarketMakingPool, created: bool):
    if created:
        system_access_header = {"Authorization": f"bearer {system_connect()}"}

        body = {
            "wallet": instance.controller_wallet,
            "contract": instance.address,
            "chain": TRADING_API_NETWORK_NAMES[instance.network]
        }

        response = requests.post(
            TRADING_API_URL + f"/api/avatea/contracts", json=body, headers=system_access_header
        )

        # TODO log
        print(response.json())
