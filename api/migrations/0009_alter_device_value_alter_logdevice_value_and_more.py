# Generated by Django 5.1.7 on 2025-04-14 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_remove_logsensor_on_off_alter_logdevice_value_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='value',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='logdevice',
            name='value',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='logsensor',
            name='value',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='value',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='value',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
