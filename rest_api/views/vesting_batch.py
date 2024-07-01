from rest_framework import viewsets

from rest_api.models import VestingBatch
from rest_api.serializers import VestingBatchSerializer


class VestingBatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Vault to be viewed or edited.
    """
    serializer_class = VestingBatchSerializer

    def get_queryset(self):
        queryset = VestingBatch.objects.all()

        project = self.request.query_params.get('project')

        if project is not None:
            queryset = queryset.filter(project=project)

        return queryset
