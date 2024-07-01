# Generated by Django 4.0.4 on 2023-03-29 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0005_remove_project_token_marketmakingpool_token_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketmakingpool',
            name='lower_preferred_price_range',
            field=models.DecimalField(decimal_places=5, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='marketmakingpool',
            name='max_buying_amount',
            field=models.DecimalField(decimal_places=5, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='marketmakingpool',
            name='max_preferred_drawdown',
            field=models.DecimalField(decimal_places=5, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='marketmakingpool',
            name='max_selling_amount',
            field=models.DecimalField(decimal_places=5, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='marketmakingpool',
            name='upper_preferred_price_range',
            field=models.DecimalField(decimal_places=5, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='marketmakingpool',
            name='volume',
            field=models.DecimalField(decimal_places=5, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=5, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='price_limit',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=18, null=True),
        ),
    ]
