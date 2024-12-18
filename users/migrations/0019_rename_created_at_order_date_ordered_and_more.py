# Generated by Django 5.1.2 on 2024-11-20 16:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0018_order_orderitem_delete_category"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="created_at",
            new_name="date_ordered",
        ),
        migrations.RemoveField(
            model_name="order",
            name="updated_at",
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_items",
                to="users.order",
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="quantity",
            field=models.PositiveIntegerField(),
        ),
    ]
