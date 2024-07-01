from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin

from rest_api.models import Project, Vault, LiquidityMaker, MarketMakingPool, UserSettings, UserAddress, Transaction, Article, VestingBatch, Vesting, Message, \
    User

TokenAdmin.raw_id_fields = ['user']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name']
    # raw_id_fields = ['owner', 'admin']
    save_as = True

@admin.register(Vault)
class VaultAdmin(admin.ModelAdmin):
    list_display = ['project', 'network', 'version']


@admin.register(LiquidityMaker)
class LiquidityMakerAdmin(admin.ModelAdmin):
    list_display = ['project', 'network', 'version']


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['market_making_pool', 'user_address']
    readonly_fields = ['algo_id']


@admin.register(MarketMakingPool)
class MarketMakingPoolAdmin(admin.ModelAdmin):
    list_display = ['project', 'network', 'version']
    readonly_fields = ['algo_id']
    save_as = True

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['address', 'country']
    exclude = ['nonce']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user_address', 'type']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['project', 'title']


@admin.register(VestingBatch)
class VestingBatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'project']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'subject', 'project']


@admin.register(Vesting)
class VestingAdmin(admin.ModelAdmin):
    list_display = ['market_making_pool', 'user_address', 'vesting_batch']
