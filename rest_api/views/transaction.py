from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_api.models import UserAddress, Project, MarketMakingPool, Vault, Transaction, UserSettings, VestingBatch, LiquidityMaker
from rest_api.serializers import TransactionSerializer


class TransactionViewSet(ReadOnlyModelViewSet,mixins.CreateModelMixin):
    """
    API endpoint that allows Transaction to be viewed or edited.
    """
    serializer_class = TransactionSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):

        transaction_type = request.data.get("type")
        user = UserAddress.objects.get(address=request.data.get("user_address"))
        contract_address = request.data.get("contract")
        value = request.data.get("value")
        full_withdrawal = request.data.get("full_withdrawal")
        project = None

        if transaction_type == 'VD':
            vault = Vault.objects.filter(address=contract_address).first()
            project = vault.project
            vault.invested.add(user)

        elif transaction_type == 'VW':
            vault = Vault.objects.filter(address=contract_address).first()
            project = vault.project
            if full_withdrawal:
                vault.invested.remove(user)

        elif transaction_type == 'VE':
            vault = Vault.objects.filter(address=contract_address).first()
            project = vault.project
            vault.invested.remove(user)

        elif transaction_type in ('VR', 'VA'):
            vault = Vault.objects.filter(address=contract_address).first()
            project = vault.project

        if transaction_type in ('LMD', 'LMB', 'LMP'):
            liquidity_maker = LiquidityMaker.objects.filter(address=contract_address).first()
            project = liquidity_maker.project
            liquidity_maker.invested.add(user)

        elif transaction_type == 'LMW':
            liquidity_maker = LiquidityMaker.objects.filter(address=contract_address).first()
            project = liquidity_maker.project
            if full_withdrawal:
                liquidity_maker.invested.remove(user)

        elif transaction_type == 'LME':
            liquidity_maker = LiquidityMaker.objects.filter(address=contract_address).first()
            project = liquidity_maker.project
            liquidity_maker.invested.remove(user)

        elif transaction_type in ('LMA', 'LMR', 'LMC', 'LML'):
            liquidity_maker = LiquidityMaker.objects.filter(address=contract_address).first()
            project = liquidity_maker.project

        elif transaction_type in ('MMBD', 'MMPD', 'MMBB'):
            market_making_pool = MarketMakingPool.objects.filter(address=contract_address).first()
            project = market_making_pool.project
            market_making_pool.invested.add(user)
            user_settings = UserSettings.objects.get_or_create(market_making_pool=market_making_pool, user_address=user)[0]
            user_settings.save()

        elif transaction_type == 'MMVD':
            market_making_pool = MarketMakingPool.objects.filter(address=contract_address).first()
            project = market_making_pool.project
            vesting_batch = VestingBatch.objects.get(pk=request.data.get("vesting_batch"))
            market_making_pool.vested.add(user, through_defaults={"vesting_batch": vesting_batch})

        elif transaction_type in ('MMVR', 'MMRT', 'MMVA'):
            market_making_pool = MarketMakingPool.objects.filter(address=contract_address).first()
            project = market_making_pool.project
            market_making_pool.invested.add(user)
            if transaction_type == 'MMRT':
                market_making_pool.vested.remove(user)

        elif transaction_type in ('MMBW', 'MMPW'):
            market_making_pool = MarketMakingPool.objects.filter(address=contract_address).first()
            project = market_making_pool.project
            if full_withdrawal:
                market_making_pool.invested.remove(user)
            user_settings = UserSettings.objects.get_or_create(market_making_pool=market_making_pool, user_address=user)[0]
            user_settings.save()

        elif transaction_type == 'MMAS':
            market_making_pool = MarketMakingPool.objects.filter(address=contract_address).first()
            project = market_making_pool.project
            user_settings = UserSettings.objects.get_or_create(market_making_pool=market_making_pool, user_address=user)[0]
            if user_settings.allow_selling and value == 'true':
                return Response({"message": "allowance already set"}, status=status.HTTP_200_OK)
            user_settings.allow_selling = True if value == 'true' else False
            user_settings.save()

        elif transaction_type == 'MMAR':
            market_making_pool = MarketMakingPool.objects.filter(address=contract_address).first()
            project = market_making_pool.project
            user_settings = UserSettings.objects.get_or_create(market_making_pool=market_making_pool, user_address=user)[0]
            user_settings.allow_releasing = True if value == 'true' else False
            user_settings.save()

        elif transaction_type == 'MMBR':
            market_making_pool = MarketMakingPool.objects.filter(address=contract_address).first()
            project = market_making_pool.project
            user_settings = UserSettings.objects.get_or_create(market_making_pool=market_making_pool, user_address=user)[0]
            user_settings.save()

        elif transaction_type == 'MMPR':
            market_making_pool = MarketMakingPool.objects.filter(address=contract_address).first()
            project = market_making_pool.project
            user_settings = UserSettings.objects.get_or_create(market_making_pool=market_making_pool, user_address=user)[0]
            user_settings.save()

        elif transaction_type == 'MMCD':
            market_making_pool = MarketMakingPool.objects.filter(address=contract_address).first()
            project = market_making_pool.project

        if project is not None:
            request.POST._mutable = True
            request.data['project'] = project.pk
            request.POST._mutable = False

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_name='bulk_create')
    def bulk_create(self, request, *args, **kwargs):

        user_addresses = request.data.get("user_addresses")
        amounts = request.data.get("amounts")

        request.POST._mutable = True

        for address, amount in zip(user_addresses, amounts):
            request.data['user_address'] = address
            request.data['amount'] = amount
            UserAddress.objects.get_or_create(address=address)

            self.create(request, *args, **kwargs)

        return Response({"message": "transactions created"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_name='bulk_create_vesting')
    def bulk_create_vesting(self, request, *args, **kwargs):

        vesting_batch = VestingBatch.objects.create(
            project=Project.objects.get(slug=request.data.get("vesting_batch_project_id")),
            name=request.data.get("vesting_batch_name"),
            created_by=request.data.get("vesting_batch_created_by"),
            start=request.data.get("vesting_batch_start"),
            cliff=request.data.get("vesting_batch_cliff"),
            duration=request.data.get("vesting_batch_duration"),
            slice=request.data.get("vesting_batch_slice"),
            revocable=request.data.get("vesting_batch_revocable")
        )

        request.POST._mutable = True
        request.data['vesting_batch'] = vesting_batch.pk

        return self.bulk_create(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Transaction.objects.all().order_by('-timestamp')
        user_address = self.request.query_params.get('user_address')
        contract = self.request.query_params.get('contract')
        project = self.request.query_params.get('project')
        transaction_type = self.request.query_params.get('type')
        if transaction_type is not None:
            queryset = queryset.filter(type=transaction_type)
        if project is not None:
            queryset = queryset.filter(project=project)
        if user_address is not None:
            queryset = queryset.filter(user_address=user_address)
        if contract is not None:
            queryset = queryset.filter(contract=contract)
        return queryset
