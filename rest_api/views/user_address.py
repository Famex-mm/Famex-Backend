import uuid

from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from web3 import Web3

from rest_api.models import UserAddress, Project, MarketMakingPool, Vault, UserSettings, LiquidityMaker
from rest_api.serializers import UserAddressSerializer, ProjectSerializer
from rest_api.utils.geo_location import get_country


class UserAddressViewSet(ReadOnlyModelViewSet, mixins.CreateModelMixin):
    """
    API endpoint that allows UserAddress to be viewed or edited.
    """
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer

    def create(self, request, *args, **kwargs):
        address = request.data.get("address")
        if UserAddress.objects.filter(address=address).exists():
            return Response(UserAddressSerializer(UserAddress.objects.get(address=address), many=False).data)
        else:
            request.POST._mutable = True
            request.data['country'] = get_country(request)
            request.data['address'] = Web3.toChecksumAddress(address)
            return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_name='retrieve_nonce')
    def retrieve_nonce(self, request, *args, **kwargs):
        user_address = self.get_object()
        nonce = uuid.uuid4().hex
        user_address.nonce = nonce
        user_address.save()
        response = {'nonce': nonce}
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_name='get_user_projects')
    def get_user_projects(self, request, *args, **kwargs):

        user_address = self.get_object()
        user_data = {}

        market_maker_invest = MarketMakingPool.objects.filter(invested=user_address)
        project_market_maker_invested = Project.objects.filter(slug__in=market_maker_invest.values('project'))

        user_settings = UserSettings.objects.filter(user_address=user_address, market_making_pool__invested=user_address, buy_sell_pressure__gt=0)
        user_settings_buying = user_settings.filter(market_making_type='buy')
        projects_buying = Project.objects.filter(slug__in=user_settings_buying.values('market_making_pool__project'))
        user_settings_selling = user_settings.filter(market_making_type='sell')
        projects_selling = Project.objects.filter(slug__in=user_settings_selling.values('market_making_pool__project'))

        market_maker_vested = MarketMakingPool.objects.filter(vested=user_address)
        project_market_maker_vested = Project.objects.filter(slug__in=market_maker_vested.values('project'))

        vault_invested = Vault.objects.filter(invested=user_address)
        project_vault_invested = Project.objects.filter(slug__in=vault_invested.values('project'))

        liquidity_maker_invested = LiquidityMaker.objects.filter(invested=user_address)
        project_liquidity_maker_invested = Project.objects.filter(slug__in=liquidity_maker_invested.values('project'))

        projects = project_market_maker_invested.union(project_market_maker_vested, project_vault_invested, project_liquidity_maker_invested)
        for project in projects:
            user_data[project.slug] = []
            if project in project_market_maker_invested:
                user_data[project.slug].append("invested")
            if project in project_market_maker_vested:
                user_data[project.slug].append("vested")
            if project in project_vault_invested:
                user_data[project.slug].append("vault")
            if project in project_liquidity_maker_invested:
                user_data[project.slug].append("liquidity")
            if project in projects_buying:
                user_data[project.slug].append("buying")
            if project in projects_selling:
                user_data[project.slug].append("selling")

        serializer = ProjectSerializer(projects, many=True)

        return Response({
            'projects': serializer.data,
            'user_data': user_data,
        })

    @action(detail=True, methods=['get'], url_name='get_user_project_data')
    def get_user_project_data(self, request, *args, **kwargs):

        user_address = self.get_object()
        user_data = []

        project_slug = self.request.query_params.get('project')
        project = Project.objects.get(pk=project_slug)

        market_making_pool = project.MarketMakingPool_of_project.first()
        vault = project.Vault_of_project.first()
        liquidity_maker = project.LiquidityMaker_of_project.first()
        user_setting = UserSettings.objects.filter(user_address=user_address, market_making_pool=market_making_pool, market_making_pool__invested=user_address,
                                                   buy_sell_pressure__gt=0)

        if market_making_pool and user_address in market_making_pool.vested.all():
            user_data.append("Vesting")
        if vault and user_address in vault.invested.all():
            user_data.append("Vault")
        if liquidity_maker and user_address in liquidity_maker.invested.all():
            user_data.append("Liquidity")
        if user_setting.exists():
            user_data.append("Sustainable Trading")

        return Response(user_data)
