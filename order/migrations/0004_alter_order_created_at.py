# Generated by Django 4.2.2 on 2023-07-19 23:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0003_alter_order_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 7, 19, 23, 36, 39, 973737, tzinfo=datetime.timezone.utc
                ),
            ),
        ),
    ]