# Generated by Django 4.0.4 on 2022-12-22 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0002_project_coming_soon_alter_project_ticker_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='signed_contract',
            field=models.BooleanField(default=True),
        ),
    ]
