# Generated by Django 5.1.7 on 2025-03-26 10:21

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('device_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=50)),
                ('brand', models.CharField(blank=True, max_length=50, null=True)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('on_off', models.BooleanField(default=False)),
                ('level', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('plan_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('and_or', models.CharField(choices=[('AND', 'And'), ('OR', 'Or')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('ssn', models.CharField(max_length=20, unique=True)),
                ('username', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='custom_user_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='custom_user_permissions', to='auth.permission')),
            ],
            options={
                'swappable': 'AUTH_USER_MODEL',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='House',
            fields=[
                ('house_id', models.AutoField(primary_key=True, serialize=False)),
                ('location', models.CharField(max_length=255)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HouseMember',
            fields=[
                ('house_member_id', models.AutoField(primary_key=True, serialize=False)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('role', models.CharField(choices=[('ADMIN', 'Admin'), ('MEMBER', 'Member')], max_length=50)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.house')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LogDevice',
            fields=[
                ('log_device_id', models.AutoField(primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=100)),
                ('on_off', models.BooleanField(blank=True, null=True)),
                ('level', models.IntegerField(blank=True, null=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.device')),
            ],
        ),
        migrations.CreateModel(
            name='PlanDevice',
            fields=[
                ('plan_device_id', models.AutoField(primary_key=True, serialize=False)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.device')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.plan')),
            ],
        ),
        migrations.AddField(
            model_name='plan',
            name='devices',
            field=models.ManyToManyField(through='api.PlanDevice', to='api.device'),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('room_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('level', models.IntegerField(blank=True, null=True)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.house')),
            ],
        ),
        migrations.AddField(
            model_name='device',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.room'),
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('schedule_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('time', models.DateTimeField()),
                ('description', models.TextField(blank=True, null=True)),
                ('action', models.CharField(max_length=100)),
                ('on_off', models.BooleanField(blank=True, null=True)),
                ('level', models.IntegerField(blank=True, null=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('sensor_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=50)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('sign', models.CharField(blank=True, max_length=10, null=True)),
                ('threshold', models.FloatField(blank=True, null=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.room')),
            ],
        ),
        migrations.CreateModel(
            name='PlanSensor',
            fields=[
                ('plan_sensor_id', models.AutoField(primary_key=True, serialize=False)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.plan')),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.sensor')),
            ],
        ),
        migrations.AddField(
            model_name='plan',
            name='sensors',
            field=models.ManyToManyField(through='api.PlanSensor', to='api.sensor'),
        ),
        migrations.CreateModel(
            name='LogSensor',
            fields=[
                ('log_sensor_id', models.AutoField(primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=100)),
                ('on_off', models.BooleanField(blank=True, null=True)),
                ('level', models.IntegerField(blank=True, null=True)),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.sensor')),
            ],
        ),
    ]
