# Generated by Django 3.2.15 on 2024-02-04 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0056_alter_productorder_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productorder',
            name='quantity',
            field=models.PositiveIntegerField(db_index=True, default=0, verbose_name='Количество продукта'),
        ),
    ]
