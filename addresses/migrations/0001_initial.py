# Generated by Django 3.2.15 on 2024-01-26 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(db_index=True, max_length=100, unique=True, verbose_name='адрес')),
                ('lng', models.FloatField(verbose_name='Долгота')),
            ],
        ),
    ]
