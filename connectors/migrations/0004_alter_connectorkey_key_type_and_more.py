# Generated by Django 4.1.4 on 2023-09-14 07:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('connectors', '0003_transformermapping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connectorkey',
            name='key_type',
            field=models.IntegerField(blank=True,
                                      choices=[(0, 'UNKNOWN'), (1, 'SENTRY_API_KEY'), (2, 'DATADOG_APP_KEY'),
                                               (3, 'DATADOG_API_KEY'), (4, 'NEWRELIC_API_KEY'), (5, 'NEWRELIC_APP_ID')],
                                      null=True),
        ),
        migrations.AlterField(
            model_name='transformermapping',
            name='decoder_type',
            field=models.IntegerField(blank=True, choices=[(0, 'UNKNOWN_DT'), (1, 'AWS_KINESIS_DECODER'),
                                                           (2, 'AWS_CLOUDWATCH_KINESIS_DECODER')], default=0,
                                      null=True),
        ),
        migrations.AlterField(
            model_name='transformermapping',
            name='transformer_type',
            field=models.IntegerField(blank=True, choices=[(0, 'UNKNOWN_TT'), (2, 'SEGMENT_DFAULT_TRANSFORMER'),
                                                           (3, 'AMPLITUDE_DEFAULT_TRANSFORMER'),
                                                           (5, 'CLOUDWATCH_JSON_LOG_TRANSFORMER')], default=0,
                                      null=True),
        ),
    ]
