# Generated by Django 3.2.15 on 2024-01-26 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0002_rename_address_place_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='lat',
            field=models.FloatField(null=True, verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='place',
            name='lng',
            field=models.FloatField(null=True, verbose_name='Долгота'),
        ),
    ]
