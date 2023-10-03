# Generated by Django 4.1.4 on 2023-03-02 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_monitortransaction_updated_at_trigger_alert'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_source',
            field=models.IntegerField(blank=True, choices=[(0, 'UNKNOWN'), (1, 'SAMPLE'), (2, 'API'), (3, 'SDK')], db_index=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='is_generated',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='eventkey',
            name='type',
            field=models.IntegerField(blank=True, choices=[(0, 'UNKNOWN'), (1, 'STRING'), (2, 'LONG'), (3, 'DOUBLE'), (4, 'BOOLEAN'), (5, 'BYTE'), (6, 'ARRAY'), (7, 'OBJECT')], db_index=True, default=0, null=True),
        ),
    ]