from datetime import datetime

from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_api.models import UserAddress, Project, Message
from rest_api.serializers import MessageSerializer
from rest_api.utils.signature import signature_checker, admin_checker


class MessageViewSet(ReadOnlyModelViewSet, mixins.CreateModelMixin):
    """
    API endpoint that allows Messages to be viewed or edited.
    """
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        response = {'message': 'Create function is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'], url_name='read')
    def read(self, request, *args, **kwargs):
        message = self.get_object()
        if message.read_at is None:
            message.read_at = datetime.now()
            message.save()
        serializer = self.get_serializer(message)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_name='delete')
    def delete(self, request, *args, **kwargs):
        signature = request.data.get("signature")
        recipient = UserAddress.objects.get(address=request.data.get("user_address"))
        signature_checker(recipient, signature)
        message = self.get_object()
        message.deleted_at = datetime.now()
        message.save()
        return Response({"message": "Message deleted"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_name='bulk_create')
    def bulk_create(self, request, *args, **kwargs):
        signature = request.data.get("signature")
        project = Project.objects.get(pk=request.data.get("project"))
        user = UserAddress.objects.get(address=request.data.get("sender"))
        admins = project.admin.all()
        admin_checker(user, admins)
        signature_checker(user, signature)

        user_addresses = request.data.get("user_addresses")
        request.POST._mutable = True

        for address in user_addresses:
            request.data['recipient'] = address
            UserAddress.objects.get_or_create(address=address)
            return super().create(request, *args, **kwargs)

        return Response({"message": "Messages created"}, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = Message.objects.filter(deleted_at=None).order_by('-sent_at')

        project = self.request.query_params.get('project')
        recipient = self.request.query_params.get('recipient')

        if project is not None:
            queryset = queryset.filter(project=project)
        if recipient is not None:
            queryset = queryset.filter(recipient=recipient)
        return queryset
