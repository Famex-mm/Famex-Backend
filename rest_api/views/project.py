from django.db.models import Avg, Count
from django.http import HttpResponseRedirect
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_api.models import UserAddress, Project, Transaction, UserSettings
from rest_api.serializers import ProjectSerializer, MarketMakingPoolSerializer, VaultSerializer, UserSettingsSerializer, LiquidityMakerSerializer
from rest_api.utils.document_signing import create_signature_form, check_signature_form
from rest_api.utils.signature import signature_checker, admin_checker
from website_backend.settings import FRONTEND_URL


class ProjectViewSet(ReadOnlyModelViewSet, mixins.UpdateModelMixin, mixins.CreateModelMixin):
    """
    API endpoint that allows Project to be viewed or edited.
    """
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.all()
        live = self.request.query_params.get('live')
        admin = self.request.query_params.get('admin')
        coming_soon = self.request.query_params.get('coming_soon')
        if live is not None:
            queryset = queryset.filter(live=live)
        if admin is not None:
            queryset = queryset.filter(admin=admin)
        if coming_soon is not None:
            queryset = queryset.filter(coming_soon=coming_soon)
        return queryset

    @action(detail=True, methods=['get'], url_name='get_project_data')
    def get_project_data(self, request, *args, **kwargs):

        project = self.get_object()

        market_making_pool = project.MarketMakingPool_of_project.first()
        market_maker_staked = market_making_pool.invested.all().count()
        vested = market_making_pool.vested.all().count()

        user_settings = market_making_pool.UserSettings_of_market_making_pool.all()

        users_selling = user_settings.filter(market_making_type='sell')
        users_selling_amount = users_selling.count()
        users_selling_pressure_avg = users_selling.aggregate(Avg('buy_sell_pressure'))['buy_sell_pressure__avg']
        users_selling_price_limit_avg = users_selling.filter(price_limit__gt=0).aggregate(Avg('price_limit'))['price_limit__avg']

        users_buying = user_settings.filter(market_making_type='buy')
        users_buying_amount = users_buying.count()
        users_buying_pressure_avg = users_buying.aggregate(Avg('buy_sell_pressure'))['buy_sell_pressure__avg']
        users_buying_price_limit_avg = users_buying.aggregate(Avg('price_limit'))['price_limit__avg']

        users_auto_releasing = user_settings.filter(allow_releasing=True).count()

        liquidity_maker = project.LiquidityMaker_of_project.first()
        liquidity_staked = liquidity_maker.invested.all().count()

        vault = project.Vault_of_project.first()
        vault_staked = vault.invested.all().count()

        return Response({
            'market_maker_staked': market_maker_staked,
            'vested': vested,
            'users_selling_amount': users_selling_amount,
            'users_selling_pressure_avg': users_selling_pressure_avg,
            'users_selling_price_limit_avg': users_selling_price_limit_avg,
            'users_buying_amount': users_buying_amount,
            'users_buying_pressure_avg': users_buying_pressure_avg,
            'users_buying_price_limit_avg': users_buying_price_limit_avg,
            'users_auto_releasing': users_auto_releasing,
            'liquidity_staked': liquidity_staked,
            'vault_staked': vault_staked,
        })

    @action(detail=True, methods=['get'], url_name='get_user_locations')
    def get_user_locations(self, request, *args, **kwargs):

        project = self.get_object()

        market_making_pool = project.MarketMakingPool_of_project.first()
        market_maker_staked = market_making_pool.invested.all()

        countries = market_maker_staked.values('country').annotate(country_count=Count('country')).order_by('country')
        data = {country['country']: country['country_count'] for country in countries}

        return Response(data)

    @action(detail=True, methods=['get'], url_name='get_vesting_data')
    def get_vesting_data(self, request, *args, **kwargs):

        project = self.get_object()

        vesting_batches = project.VestingBatch_of_project.all()
        data = {}
        for batch in vesting_batches:
            vestings = batch.Vesting_of_vesting_batch.all()
            users = vestings.values_list('user_address')
            transactions = Transaction.objects.filter(project=project, user_address__in=users)

            data[batch.name] = {
                'total': vestings.count(),
                'released': transactions.filter(type__in=['MMVR', 'MMVA']).values_list('user_address').distinct().count(),
                'withdrawn': transactions.filter(type='MMBW').values_list('user_address').distinct().count(),
                'liquidity': transactions.filter(type='LMB').values_list('user_address').distinct().count(),
                'sold': transactions.filter(type='MMAS').values_list('user_address').distinct().count(),
            }

        return Response(data)

    def update(self, request, *args, **kwargs):
        signature = request.data.get("signature")
        user = UserAddress.objects.get(address=request.data.get("user_address"))
        admins = self.get_object().admin.all()
        admin_checker(user, admins)
        signature_checker(user, signature)
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        signature = request.data.get("signature")
        user = UserAddress.objects.get(address=request.data.get("owner"))
        signature_checker(user, signature)

        request.POST._mutable = True
        request.data['signature_id'] = create_signature_form(request.data)
        request.data['admin'] = request.data.get("owner")
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_name='receive_signature_callback')
    def receive_signature_callback(self, request, *args, **kwargs):
        project = self.get_object()
        event = self.request.query_params.get('event')
        personal_signature_id = self.request.query_params.get('signature_id')
        if event == 'signature_request_signed' and not project.signed_contract:
            check_signature_form(project.signature_id, personal_signature_id)
            project.signed_contract = True
            project.save()

        return HttpResponseRedirect(redirect_to=f'{FRONTEND_URL}management/{project.slug}')

    @action(detail=True, methods=['get'], url_name='get_addresses')
    def get_addresses(self, request, *args, **kwargs):

        project = self.get_object()
        data = {}

        vesting_batches = project.VestingBatch_of_project.all()
        vesting_batches_data = {}
        for vesting_batch in vesting_batches:
            vesting_batches_data[vesting_batch.name] = list(vesting_batch.Vesting_of_vesting_batch.all().values_list('user_address', flat=True))
        data['Vesting Batches'] = vesting_batches_data

        market_making_pools = project.MarketMakingPool_of_project.all()
        market_making_pool_data = {}
        for market_making_pool in market_making_pools:
            market_making_pool_data[str(market_making_pool)] = {
                "Invested": list(market_making_pool.invested.all().values_list('address', flat=True)),
                "Vested": list(market_making_pool.invested.all().values_list('address', flat=True))
            }
        data['Market Making Pools'] = market_making_pool_data

        vault = project.Vault_of_project.all().first()
        if vault is not None:
            data['Vault'] = list(vault.invested.all().values_list('address', flat=True))

        liquidity_maker = project.LiquidityMaker_of_project.all().first()
        if liquidity_maker is not None:
            data['Liquidity Maker'] = list(liquidity_maker.invested.all().values_list('address', flat=True))

        return Response({
            'data': data,
        })

    def retrieve(self, request, *args, **kwargs):

        network = self.request.query_params.get('network')
        user_address = self.request.query_params.get('user_address')

        project = self.get_object()

        if network is not None:
            market_making_pool = project.MarketMakingPool_of_project.filter(network=network).first()
            vault = project.Vault_of_project.filter(network=network).first()
            liquidity_maker = project.LiquidityMaker_of_project.filter(network=network).first()
        else:
            market_making_pool = project.MarketMakingPool_of_project.all().first()
            vault = project.Vault_of_project.all().first()
            liquidity_maker = project.LiquidityMaker_of_project.all().first()

        if market_making_pool is not None:
            user_settings = market_making_pool.UserSettings_of_market_making_pool.filter(user_address=user_address).first()
        else:
            user_settings = UserSettings.objects.none().first()

        user_settings_serialized = UserSettingsSerializer(user_settings, many=False)
        project_serialized = ProjectSerializer(project, many=False)
        market_making_pool_serializer = MarketMakingPoolSerializer(market_making_pool, many=False)
        vault_serializer = VaultSerializer(vault, many=False)
        liquidity_maker_serializer = LiquidityMakerSerializer(liquidity_maker, many=False)

        return Response({
            'project': project_serialized.data,
            'marketMakingPool': market_making_pool_serializer.data,
            'UserSettings': user_settings_serialized.data,
            'vault': vault_serializer.data,
            'liquidityMaker': liquidity_maker_serializer.data,
        })
