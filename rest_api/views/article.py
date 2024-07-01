from rest_framework.viewsets import ModelViewSet

from rest_api.models import UserAddress, Project, Article
from rest_api.serializers import ArticleSerializer
from rest_api.utils.signature import signature_checker, admin_checker


class ArticleViewSet(ModelViewSet):
    """
    API endpoint that allows Article to be viewed or edited.
    """
    serializer_class = ArticleSerializer

    def update(self, request, *args, **kwargs):
        signature = request.data.get("signature")
        user = UserAddress.objects.get(address=request.data.get("user_address"))
        admins = self.get_object().project.admin.all()
        admin_checker(user, admins)
        signature_checker(user, signature)
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        signature = request.data.get("signature")
        project = Project.objects.get(pk=request.data.get("project"))
        user = UserAddress.objects.get(address=request.data.get("user_address"))
        admins = project.admin.all()
        admin_checker(user, admins)
        signature_checker(user, signature)
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        signature = request.data.get("signature")
        user = UserAddress.objects.get(address=request.data.get("user_address"))
        admins = self.get_object().project.admin.all()
        admin_checker(user, admins)
        signature_checker(user, signature)
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Article.objects.all()

        project = self.request.query_params.get('project')

        if project is not None:
            queryset = queryset.filter(project=project)
        return queryset
