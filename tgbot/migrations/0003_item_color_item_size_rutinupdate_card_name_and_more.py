# Generated by Django 4.0.7 on 2022-08-23 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0002_rutinupdate_remove_user_is_banned_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='color',
            field=models.CharField(blank=True, default='', max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='size',
            field=models.CharField(blank=True, default='', max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='rutinupdate',
            name='card_name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
