from rest_framework import serializers

from rest_api.models import UserAddress, Project, MarketMakingPool, Vault, Transaction, UserSettings, Article, VestingBatch, Vesting, LiquidityMaker, Message


class CustomSerializer(serializers.ModelSerializer):
    def get_field_names(self, declared_fields, info):

        expanded_fields = super(CustomSerializer, self).get_field_names(declared_fields, info)
        if getattr(self.Meta, 'extra_fields', None):
            expanded_fields += self.Meta.extra_fields
        if getattr(self.Meta, 'remove_fields', None):
            for field in self.Meta.remove_fields:
                expanded_fields.remove(field)
        return expanded_fields


class UserAddressSerializer(CustomSerializer):
    num_unread_messages = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserAddress
        fields = '__all__'
        remove_fields = ['nonce']
        extra_fields = ['Project_of_admin']
        read_only_fields = ['Project_of_admin']
        extra_kwargs = {
            "country": {'write_only': True},
        }


class ProjectSerializer(CustomSerializer):
    networks = serializers.JSONField(allow_null=True, read_only=True)
    liquidity = serializers.BooleanField(source='LiquidityMaker_of_project.count', read_only=True)
    vault = serializers.BooleanField(source='Vault_of_project.count', read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        extra_kwargs = {
            "contact_name": {'write_only': True},
            "contact_email": {'write_only': True},
            "contact_phone": {'write_only': True},
            "contact_telegram": {'write_only': True},
            "contact_company": {'write_only': True},
            "contact_street": {'write_only': True},
            "contact_city": {'write_only': True},
            "contact_state": {'write_only': True},
            "contact_postal": {'write_only': True},
            "contact_country": {'write_only': True},
            "signature_id": {'write_only': True},
        }


class MarketMakingPoolSerializer(CustomSerializer):
    num_invested = serializers.IntegerField(source='invested.count', read_only=True)
    num_vested = serializers.IntegerField(source='vested.count', read_only=True)
    name = serializers.CharField(source='project.name', read_only=True)
    image = serializers.ImageField(source='project.image', read_only=True)
    banner = serializers.ImageField(source='project.banner', read_only=True)

    class Meta:
        model = MarketMakingPool
        fields = '__all__'
        remove_fields = ['invested', 'vested']


class VaultSerializer(CustomSerializer):
    num_invested = serializers.IntegerField(source='invested.count', read_only=True)
    name = serializers.CharField(source='project.name', read_only=True)
    image = serializers.ImageField(source='project.image', read_only=True)
    banner = serializers.ImageField(source='project.banner', read_only=True)

    class Meta:
        model = Vault
        fields = '__all__'
        remove_fields = ['invested']


class LiquidityMakerSerializer(CustomSerializer):
    num_invested = serializers.IntegerField(source='invested.count', read_only=True)
    name = serializers.CharField(source='project.name', read_only=True)
    image = serializers.ImageField(source='project.image', read_only=True)
    banner = serializers.ImageField(source='project.banner', read_only=True)
    ticker = serializers.CharField(source='project.ticker', read_only=True)
    token = serializers.CharField(source='project.token', read_only=True)

    class Meta:
        model = LiquidityMaker
        fields = '__all__'
        remove_fields = ['invested']


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='project.name', read_only=True)
    image = serializers.ImageField(source='project.image', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='project.image', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class VestingBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = VestingBatch
        fields = '__all__'


class VestingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vesting
        fields = '__all__'


# ---------------------- Serializers for data transfer to market making algo ----------------------

class MarketMakingPoolAlgoSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(source='project.slug', read_only=True)
    base_token = serializers.CharField(source='token', read_only=True)
    owner = serializers.CharField(source='project.owner.address', read_only=True)

    class Meta:
        model = MarketMakingPool
        fields = ['slug',
                  'base_token',
                  'paired_token',
                  'address',
                  'version',
                  'network',
                  'max_preferred_drawdown',
                  'lower_preferred_price_range',
                  'upper_preferred_price_range',
                  'max_selling_amount',
                  'max_buying_amount',
                  'volume',
                  'owner']


class UserSettingsAlgoSerializer(serializers.ModelSerializer):
    market_making_pool = serializers.IntegerField(source='market_making_pool.algo_id', read_only=True)

    class Meta:
        model = UserSettings
        fields = ['market_making_pool',
                  'user_address',
                  'market_making_type',
                  'buy_sell_pressure',
                  'price_limit',
                  'trading_until',
                  'allow_releasing']
