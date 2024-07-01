import requests

from rest_api.models import MarketMakingPool, UserSettings
from rest_api.serializers import MarketMakingPoolAlgoSerializer, UserSettingsAlgoSerializer
from website_backend.settings import ALGO_URL, ALGO_TOKEN


def update_user_settings(instance: UserSettings, created: bool):
    token_header = {"Authorization": f"Token {ALGO_TOKEN}"}

    body = UserSettingsAlgoSerializer(instance, many=False).data
    print(body)

    if created or not instance.algo_id:
        response = requests.post(f"{ALGO_URL}UserSettings/", json=body, headers=token_header)
        instance.algo_id = int(response.json()['id'])
        instance.save()
    else:
        response = requests.patch(f"{ALGO_URL}UserSettings/{instance.algo_id}/", json=body, headers=token_header)

    # TODO log
    print(response.json())


def update_market_making_pool(instance: MarketMakingPool, created: bool):
    token_header = {"Authorization": f"Token {ALGO_TOKEN}"}

    body = MarketMakingPoolAlgoSerializer(instance, many=False).data
    print(body)

    if created or not instance.algo_id:
        response = requests.post(f"{ALGO_URL}MarketMakingPool/", json=body, headers=token_header)
        instance.algo_id = int(response.json()['id'])
        instance.save()
    else:
        response = requests.patch(f"{ALGO_URL}MarketMakingPool/{instance.algo_id}/", json=body, headers=token_header)

    # TODO log
    print(response.json())


def retrieve_tickers_from_algo(instance: MarketMakingPool):
    token_header = {"Authorization": f"Token {ALGO_TOKEN}"}

    response = requests.get(f"{ALGO_URL}MarketMakingPool/{instance.algo_id}/retrieve_tickers/", headers=token_header)
    return response.json()
