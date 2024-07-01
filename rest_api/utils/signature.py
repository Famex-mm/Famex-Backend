import binascii
import uuid

from django.db.models import QuerySet
from eth_account.messages import defunct_hash_message
from rest_framework.exceptions import ValidationError
from web3.auto import w3

from rest_api.models import UserAddress


def signature_checker(user: UserAddress, signature: str):
    try:
        nonce = user.nonce
        user.nonce = uuid.uuid4().hex
        user.save()

        original_message = "Signature in order to authenticate:  " + nonce
        message_hash = defunct_hash_message(text=original_message)
        signer = w3.eth.account.recoverHash(message_hash, signature=signature)
        assert user.address == signer

    except (TypeError, binascii.Error, AssertionError):
        raise ValidationError(
            {'permission denied': "Signature does not correspond to wallet"}
        )


def admin_checker(user: UserAddress, admins: QuerySet):
    try:
        assert admins.filter(pk=user).exists()

    except AssertionError:
        raise ValidationError(
            {'permission denied': "account does not correspond to admin"}
        )
