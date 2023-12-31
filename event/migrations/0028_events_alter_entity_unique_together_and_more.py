# Generated by Django 4.1.4 on 2023-09-18 09:22

import clickhouse_backend.models
from django.db import migrations, models
import django.db.models.deletion
import prototype.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_account_is_whitelisted'),
        ('event', '0027_events_alter_event_event_source_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='entity',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='entity',
            name='is_generated',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='type',
            field=models.IntegerField(blank=True, choices=[(0, 'UNKNOWN'), (1, 'DEFAULT'), (2, 'FUNNEL')], db_index=True, default=1, null=True),
        ),
        migrations.AddField(
            model_name='monitor',
            name='is_generated',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_source',
            field=models.IntegerField(blank=True, choices=[(0, 'UNKNOWN'), (1, 'SAMPLE'), (2, 'API'), (3, 'SDK'), (4, 'SEGMENT'), (5, 'AMPLITUDE'), (6, 'SNS'), (7, 'CLOUDWATCH')], db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='eventtype',
            name='event_sources',
            field=prototype.fields.ChoiceArrayField(base_field=models.IntegerField(blank=True, choices=[(0, 'UNKNOWN'), (1, 'SAMPLE'), (2, 'API'), (3, 'SDK'), (4, 'SEGMENT'), (5, 'AMPLITUDE'), (6, 'SNS'), (7, 'CLOUDWATCH')], null=True), default=list, size=None),
        ),
        migrations.AlterUniqueTogether(
            name='entity',
            unique_together={('account', 'name', 'type')},
        ),
        migrations.CreateModel(
            name='EntityMonitorMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(blank=True, default=True, null=True)),
                ('is_generated', models.BooleanField(blank=True, default=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.account')),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.entity')),
                ('monitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.monitor')),
            ],
            options={
                'unique_together': {('account', 'entity', 'monitor')},
            },
        ),
        migrations.AddField(
            model_name='entity',
            name='entity_monitors',
            field=models.ManyToManyField(related_name='entity_monitors', through='event.EntityMonitorMapping', to='event.monitor'),
        ),
    ]
