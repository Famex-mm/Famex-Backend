from rest_framework import viewsets

from rest_api.models import Vault
from rest_api.serializers import VaultSerializer


class VaultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Vault to be viewed or edited.
    """
    serializer_class = VaultSerializer

    def get_queryset(self):
        queryset = Vault.objects.all()

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
