from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_api.models import UserAddress, UserSettings, MarketMakingPool
from rest_api.serializers import UserSettingsSerializer
from rest_api.utils.signature import signature_checker


class UserSettingsViewSet(ReadOnlyModelViewSet, mixins.UpdateModelMixin, mixins.CreateModelMixin):
    """
    API endpoint that allows UserSettings to be viewed or edited.
    """
    serializer_class = UserSettingsSerializer

    def update(self, request, *args, **kwargs):
        signature = request.data.get("signature")
        user = self.get_object().user_address
        signature_checker(user, signature)
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        signature = request.data.get("signature")
        user = UserAddress.objects.get(address=request.data.get("user_address"))
        signature_checker(user, signature)

        market_making_pool = MarketMakingPool.objects.get(id=request.data.get("market_making_pool"))
        user_setting_query = UserSettings.objects.filter(user_address=user, market_making_pool=market_making_pool)

        if user_setting_query.exists():
            instance = user_setting_query.first()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)

        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        queryset = UserSettings.objects.all()

        user_address = self.request.query_params.get('user_address')
        market_making_pool_address = self.request.query_params.get('market_making_pool_address')

        if user_address is not None:
            queryset = queryset.filter(user_address=user_address)
        if market_making_pool_address is not None:
            queryset = queryset.filter(market_making_pool__address=market_making_pool_address)
        return queryset
