from rest_framework import viewsets

from rest_api.models import LiquidityMaker
from rest_api.serializers import LiquidityMakerSerializer


class LiquidityMakerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows LiquidityMaker to be viewed or edited.
    """
    serializer_class = LiquidityMakerSerializer

    def get_queryset(self):
        queryset = LiquidityMaker.objects.all()

        invested = self.request.query_params.get('invested')
        saved = self.request.query_params.get('saved')
        live = self.request.query_params.get('live')
        network = self.request.query_params.get('network')

        if invested is not None:
            queryset = queryset.filter(invested=invested)
        if saved is not None:
            queryset = queryset.filter(saved=saved)
        if live is not None:
            queryset = queryset.filter(live=True)
        if network is not None:
            queryset = queryset.filter(network=network)
        return queryset
