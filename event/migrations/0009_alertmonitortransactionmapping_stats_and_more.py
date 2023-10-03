# Generated by Django 4.1.4 on 2023-03-08 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0008_alert_stats'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertmonitortransactionmapping',
            name='stats',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='alertmonitortransactionmapping',
            name='type',
            field=models.IntegerField(blank=True, choices=[(0, 'UNKNOWN'), (1, 'MISSED_TRANSACTION'), (2, 'DELAYED_TRANSACTION')], db_index=True, default=0, null=True),
        ),
    ]