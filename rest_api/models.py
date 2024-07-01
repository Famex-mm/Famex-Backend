from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from website_backend.constants import NETWORK_CHOICES, DEFAULT_NETWORK


def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class User(AbstractUser):
    pass


class UserAddress(models.Model):
    address = models.CharField(primary_key=True, max_length=42)
    created_at = models.DateTimeField(auto_now_add=True)
    nonce = models.CharField(blank=True, max_length=42, default='')
    country = models.CharField(blank=True, max_length=30, default='')

    class Meta:
        verbose_name_plural = "UserAddresses"

    def num_unread_messages(self):
        return self.Message_of_recipient.filter(read_at=None).count()

    def __str__(self):
        return self.address


class Project(models.Model):
    slug = models.SlugField(primary_key=True, max_length=50)
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(UserAddress, on_delete=models.PROTECT, related_name='Project_of_owner')
    admin = models.ManyToManyField(UserAddress, blank=True, related_name='Project_of_admin')
    ticker = models.CharField(max_length=8, blank=True, default='')
    live = models.BooleanField(default=False)
    coming_soon = models.BooleanField(default=False)
    description = models.TextField(max_length=2000, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    website = models.URLField(blank=True, max_length=400, default='')
    whitepaper = models.URLField(blank=True, max_length=400, default='')
    audit = models.URLField(blank=True, max_length=400, default='')
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    banner = models.ImageField(upload_to=upload_to, blank=True, null=True)
    signature_id = models.CharField(max_length=64, blank=True, default='')
    signed_contract = models.BooleanField(default=True)
    networks = models.JSONField(default=list, null=True, blank=True)
    data = models.JSONField(default=dict, null=True, blank=True)

    # Social Fields
    social_linkedin = models.URLField(blank=True, max_length=400, default='')
    social_facebook = models.URLField(blank=True, max_length=400, default='')
    social_github = models.URLField(blank=True, max_length=400, default='')
    social_telegram = models.URLField(blank=True, max_length=400, default='')
    social_discord = models.URLField(blank=True, max_length=400, default='')
    social_medium = models.URLField(blank=True, max_length=400, default='')
    social_twitter = models.URLField(blank=True, max_length=400, default='')

    # Contact Fields
    contact_name = models.CharField(max_length=100, blank=True, default='')
    contact_email = models.CharField(max_length=100, blank=True, default='')
    contact_phone = models.CharField(max_length=15, blank=True, default='')
    contact_telegram = models.CharField(max_length=32, blank=True, default='')
    contact_company = models.CharField(max_length=100, blank=True, default='')
    contact_street = models.CharField(max_length=100, blank=True, default='')
    contact_city = models.CharField(max_length=32, blank=True, default='')
    contact_state = models.CharField(max_length=32, blank=True, default='')
    contact_postal = models.CharField(max_length=32, blank=True, default='')
    contact_country = models.CharField(max_length=32, blank=True, default='')

    def __str__(self):
        return self.name


class MarketMakingPool(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='MarketMakingPool_of_project')
    address = models.CharField(max_length=42)
    token = models.CharField(max_length=42, blank=True, default='')
    controller_wallet = models.CharField(max_length=42)
    version = models.CharField(max_length=5, default='1.0')
    live = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paired_token = models.CharField(max_length=42)
    paired_token_image = models.URLField(blank=True, max_length=400, default='')
    paired_token_ticker = models.CharField(max_length=8)
    invested = models.ManyToManyField(UserAddress, blank=True, related_name='MarketMakingPool_of_invested')
    vested = models.ManyToManyField(UserAddress, blank=True, related_name='MarketMakingPool_of_vested', through='Vesting')
    network = models.CharField(max_length=100, choices=NETWORK_CHOICES, default=DEFAULT_NETWORK)
    algo_id = models.IntegerField(null=True, blank=True)

    # Market Making settings
    volume = models.DecimalField(max_digits=18, decimal_places=5, default=0)
    lower_preferred_price_range = models.DecimalField(max_digits=18, decimal_places=5, default=0)
    upper_preferred_price_range = models.DecimalField(max_digits=18, decimal_places=5, default=0)
    max_selling_amount = models.DecimalField(max_digits=18, decimal_places=5, default=0)
    max_buying_amount = models.DecimalField(max_digits=18, decimal_places=5, default=0)
    max_preferred_drawdown = models.DecimalField(max_digits=18, decimal_places=5, default=0)

    class Meta:
        unique_together = ('project', 'network', 'version')

    def __str__(self):
        return str(self.project) + ' - network: ' + str(self.network)


class Vesting(models.Model):
    market_making_pool = models.ForeignKey(MarketMakingPool, on_delete=models.PROTECT, related_name='Vesting_of_market_making_pool')
    user_address = models.ForeignKey(UserAddress, on_delete=models.PROTECT, related_name='Vesting_of_user_address')
    vesting_batch = models.ForeignKey("VestingBatch", on_delete=models.PROTECT, related_name='Vesting_of_vesting_batch')


class VestingBatch(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='VestingBatch_of_project')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=42)
    name = models.CharField(max_length=200)
    start = models.IntegerField()
    cliff = models.IntegerField()
    duration = models.IntegerField()
    slice = models.IntegerField()
    revocable = models.BooleanField()

    def __str__(self):
        return str(self.name)


class UserSettings(models.Model):
    MARKET_MAKING_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    market_making_pool = models.ForeignKey(MarketMakingPool, on_delete=models.PROTECT, related_name='UserSettings_of_market_making_pool')
    user_address = models.ForeignKey(UserAddress, on_delete=models.PROTECT, related_name='UserSettings_of_user_address')
    market_making_type = models.CharField(max_length=10, choices=MARKET_MAKING_TYPES, default='sell')
    buy_sell_pressure = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    price_limit = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    trading_until = models.DateTimeField(null=True, blank=True)
    allow_selling = models.BooleanField(default=False)
    allow_releasing = models.BooleanField(default=False)
    algo_id = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('market_making_pool', 'user_address',)
        verbose_name_plural = "UsersSettings"


class Vault(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='Vault_of_project')
    address = models.CharField(max_length=42)
    version = models.CharField(max_length=5, default='1.0')
    live = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    invested = models.ManyToManyField(UserAddress, blank=True, related_name='Vault_of_invested')
    network = models.CharField(max_length=100, choices=NETWORK_CHOICES, default=DEFAULT_NETWORK)

    class Meta:
        unique_together = ('project', 'network', 'version')

    def __str__(self):
        return str(self.project)


class LiquidityMaker(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='LiquidityMaker_of_project')
    address = models.CharField(max_length=42)
    paired_token = models.CharField(max_length=42)
    paired_token_image = models.URLField(blank=True, max_length=400, default='')
    paired_token_ticker = models.CharField(max_length=8)
    pair_address = models.CharField(max_length=42)
    version = models.CharField(max_length=5, default='1.0')
    live = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    invested = models.ManyToManyField(UserAddress, blank=True, related_name='LiquidityMaker_of_invested')
    network = models.CharField(max_length=100, choices=NETWORK_CHOICES, default=DEFAULT_NETWORK)

    class Meta:
        unique_together = ('project', 'network', 'version')

    def __str__(self):
        return str(self.project)


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('VD', 'Vault Deposit'),
        ('VW', 'Vault Withdrawal'),
        ('VE', 'Vault Exit'),
        ('VR', 'Vault Rewards'),
        ('VA', 'Vault Reward Adding'),

        ('LMD', 'Liquidity Maker LP Deposit'),
        ('LMB', 'Liquidity Maker Base Deposit'),
        ('LMP', 'Liquidity Maker Paired Deposit'),
        ('LMW', 'Liquidity Maker Withdrawal'),
        ('LME', 'Liquidity Maker Exit'),
        ('LMA', 'Liquidity Maker Reward Adding'),
        ('LMR', 'Liquidity Maker Rewards Claiming'),
        ('LMC', 'Liquidity Maker Liquidity Compound'),
        ('LML', 'Liquidity Maker Liquidity Reward Adding'),

        ('MMBD', 'Market Making Base Deposit'),
        ('MMPD', 'Market Making Paired Deposit'),
        ('MMBB', 'Market Making Base Batch'),
        ('MMVD', 'Market Making Vesting Deposit'),
        ('MMVR', 'Market Making Vesting Release'),
        ('MMVA', 'Market Making Vesting Automated Release'),
        ('MMRT', 'Market Making Revoke Tokens'),
        ('MMBW', 'Market Making Base Withdrawal'),
        ('MMPW', 'Market Making Paired Withdrawal'),
        ('MMAS', 'Market Making Allow Selling'),
        ('MMAR', 'Market Making Allow Releasing'),
        ('MMBR', 'Market Making Base Staking Ratio'),
        ('MMPR', 'Market Making Paired Staking Ratio'),
        ('MMCD', 'Market Making Contract Deployment'),
    ]

    contract = models.CharField(max_length=42)
    user_address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL, related_name='Transaction_of_user_address', null=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='Transaction_of_project', blank=True, null=True)
    type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=18, decimal_places=5, default=0, blank=True)
    value = models.CharField(max_length=30, default='', blank=True)
    hash = models.CharField(max_length=66, default='', blank=True)
    network = models.CharField(max_length=100, choices=NETWORK_CHOICES, default=DEFAULT_NETWORK)
    full_withdrawal = models.BooleanField(default=False)

    def __str__(self):
        return str(self.type) + ', ' + str(self.amount)


class Article(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='Article_of_project')
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=2000, default='', blank=True)
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    link = models.URLField(blank=True, max_length=400, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    subject = models.CharField(max_length=140)
    body = models.TextField()
    sender = models.ForeignKey(UserAddress, related_name='Message_of_sender', on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='Message_of_project')
    recipient = models.ForeignKey(UserAddress, related_name='Message_of_recipient', null=True, blank=True, on_delete=models.SET_NULL)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
