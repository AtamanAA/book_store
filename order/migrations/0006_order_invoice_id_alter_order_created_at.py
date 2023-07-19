# Generated by Django 4.2.2 on 2023-07-17 22:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0005_order_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="invoice_id",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 7, 18, 1, 52, 24, 359084)
            ),
        ),
    ]
