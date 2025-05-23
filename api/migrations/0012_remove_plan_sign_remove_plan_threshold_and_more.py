# Generated by Django 5.1.7 on 2025-05-05 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_rename_user_id_device_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='sign',
        ),
        migrations.RemoveField(
            model_name='plan',
            name='threshold',
        ),
        migrations.AddField(
            model_name='plandevice',
            name='on_off',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='plansensor',
            name='sign',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='plansensor',
            name='threshold',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
