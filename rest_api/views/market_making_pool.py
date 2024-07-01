from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_api.models import UserAddress, Project, MarketMakingPool
from rest_api.serializers import MarketMakingPoolSerializer
from rest_api.utils.algo_connection import retrieve_tickers_from_algo
from rest_api.utils.contract_validity import check_validity_contract
from rest_api.utils.signature import signature_checker, admin_checker


class MarketMakingPoolViewSet(ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    """
    API endpoint that allows MarketMakingPool to be viewed or edited.
    """
    serializer_class = MarketMakingPoolSerializer

    @action(detail=True, methods=['get'], url_name='retrieve_tickers')
    def retrieve_tickers(self, request, *args, **kwargs):
        market_making_pool = self.get_object()
        return Response(retrieve_tickers_from_algo(market_making_pool), status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        signature = request.data.get("signature")
        user = UserAddress.objects.get(address=request.data.get("user_address"))
        admins = self.get_object().project.admin.all()
        admin_checker(user, admins)
        signature_checker(user, signature)
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        market_making_pool_address = request.data.get("address")
        network = request.data.get("network")
        creator = check_validity_contract(market_making_pool_address, network)
        project = Project.objects.get(pk=request.data.get("project"))
        project.networks.append(request.data.get("network"))
        project.save()
        admins = project.admin.all()
        admin_checker(creator, admins)
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        queryset = MarketMakingPool.objects.all()

        invested = self.request.query_params.get('invested')
        vested = self.request.query_params.get('vested')
        saved = self.request.query_params.get('saved')
        live = self.request.query_params.get('live')
        network = self.request.query_params.get('network')
        address = self.request.query_params.get('address')

        if invested is not None:
            queryset = queryset.filter(invested=invested)
        if saved is not None:
            queryset = queryset.filter(saved=saved)
        if vested is not None:
            queryset = queryset.filter(vested=vested)
        if live is not None:
            queryset = queryset.filter(live=True)
        if network is not None:
            queryset = queryset.filter(network=network)
        if address is not None:
            queryset = queryset.filter(address=address)
        return queryset
