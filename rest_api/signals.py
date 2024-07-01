from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_api.models import MarketMakingPool, UserSettings
from rest_api.utils.algo_connection import update_user_settings, update_market_making_pool
from rest_api.utils.trading_api_connection import update_algo_creation


@receiver(post_save, sender=UserSettings)
def update_user_settings_receiver(instance: UserSettings, created: bool, **kwargs):
    post_save.disconnect(update_user_settings_receiver, sender=UserSettings)
    update_user_settings(instance, created)
    post_save.connect(update_user_settings_receiver, sender=UserSettings)


@receiver(post_save, sender=MarketMakingPool)
def update_market_making_pool_receiver(instance: MarketMakingPool, created: bool, **kwargs):
    post_save.disconnect(update_market_making_pool_receiver, sender=MarketMakingPool)
    update_market_making_pool(instance, created)
    post_save.connect(update_market_making_pool_receiver, sender=MarketMakingPool)


@receiver(post_save, sender=MarketMakingPool)
def update_algo_creation_receiver(instance: MarketMakingPool, created: bool, **kwargs):
    update_algo_creation(instance, created)
