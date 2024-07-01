from rest_framework import viewsets

from rest_api.models import Vesting
from rest_api.serializers import VestingSerializer


class VestingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Vault to be viewed or edited.
    """
    serializer_class = VestingSerializer

    def get_queryset(self):
        queryset = Vesting.objects.all()

        vesting_batch = self.request.query_params.get('vesting_batch')

        if vesting_batch is not None:
            queryset = queryset.filter(vesting_batch=vesting_batch)

        return queryset
