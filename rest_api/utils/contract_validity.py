import json
import os

from rest_framework.exceptions import ValidationError
from web3 import Web3

from website_backend.constants import ADDRESSES, NETWORK_PROVIDERS
from website_backend.settings import BASE_DIR


def check_validity_contract(market_making_pool_address: str, network: str):
    try:
        market_making_pool_address = Web3.toChecksumAddress(market_making_pool_address)
        path = os.path.join(BASE_DIR, "assets/MarketMakerDeployer.json")
        with open(path) as f:
            info_json = json.load(f)
        abi = info_json["abi"]

        w3 = Web3(Web3.HTTPProvider(NETWORK_PROVIDERS[network]))
        market_making_pool_deployer = w3.eth.contract(address=ADDRESSES[network]["MarketMakerDeployer"], abi=abi)

        assert market_making_pool_deployer.functions.isContractCreated(market_making_pool_address).call()

        return get_owner_contract(market_making_pool_address, network)
    except (AssertionError, ValueError):
        raise ValidationError(
            {'permission denied': "Contract address is not supported"}
        )


def get_owner_contract(market_making_pool_address: str, network: str) -> str:
    market_making_pool_address = Web3.toChecksumAddress(market_making_pool_address)
    path = os.path.join(BASE_DIR, "assets/MarketMaker.json")

    with open(path) as f:
        info_json = json.load(f)
    abi = info_json["abi"]

    w3 = Web3(Web3.HTTPProvider(NETWORK_PROVIDERS[network]))
    market_making_pool = w3.eth.contract(address=market_making_pool_address, abi=abi)

    return market_making_pool.functions.owner().call()
