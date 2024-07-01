"""website_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from rest_api import views

router = routers.DefaultRouter()
router.register(r'UserAddress', views.UserAddressViewSet, basename='UserAddress')
router.register(r'Project', views.ProjectViewSet, basename='Project')
router.register(r'MarketMakingPool', views.MarketMakingPoolViewSet, basename='MarketMakingPool')
router.register(r'Vault', views.VaultViewSet, basename='Vault')
router.register(r'Transaction', views.TransactionViewSet, basename='Transaction')
router.register(r'UserSettings', views.UserSettingsViewSet, basename='UserSettings')
router.register(r'Article', views.ArticleViewSet, basename='Article')
router.register(r'VestingBatch', views.VestingBatchViewSet, basename='VestingBatch')
router.register(r'Vesting', views.VestingViewSet, basename='Vesting')
router.register(r'LiquidityMaker', views.LiquidityMakerViewSet, basename='LiquidityMaker')
router.register(r'Message', views.MessageViewSet, basename='Message')

urlpatterns = [
                  path('', include(router.urls)),
                  path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
