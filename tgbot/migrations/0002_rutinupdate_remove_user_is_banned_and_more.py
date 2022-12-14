# Generated by Django 4.0.7 on 2022-08-16 00:16

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RutinUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('today_price_in_tl', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('card_no', models.CharField(blank=True, max_length=32, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_banned',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_moderator',
        ),
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.PositiveBigIntegerField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('all_to_pay', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('is_aproved', models.BooleanField(default=False)),
                ('is_checkedout', models.BooleanField(default=False)),
                ('is_canceled', models.BooleanField(default=False)),
                ('is_finished', models.BooleanField(default=False)),
                ('order_tracking', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.user')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sales_link', models.CharField(blank=True, default='', max_length=1024, null=True)),
                ('price_per_unit_in_tl', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('count', models.PositiveIntegerField(default=1)),
                ('detales', models.CharField(blank=True, default='', max_length=1024, null=True)),
                ('to_pay', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.order')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]
