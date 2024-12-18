# Generated by Django 5.1.2 on 2024-11-26 14:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0020_alter_serviceitem_service_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_method",
            field=models.CharField(
                blank=True,
                choices=[("credit_card", "Credit Card"), ("cod", "Cash on Delivery")],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("paid", "Paid")],
                default="pending",
                max_length=10,
            ),
        ),
    ]
