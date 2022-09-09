# Generated by Django 4.0.7 on 2022-08-25 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0004_remove_order_order_tracking_order_is_paid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_available',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.CharField(default='JFbHvJZm', editable=False, max_length=8, primary_key=True, serialize=False, unique=True),
        ),
    ]
