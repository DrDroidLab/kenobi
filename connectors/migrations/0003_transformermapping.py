# Generated by Django 4.1.4 on 2023-05-09 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_account_owner'),
        ('connectors', '0002_alter_connector_connector_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransformerMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decoder_type', models.IntegerField(blank=True, choices=[(0, 'UNKNOWN_DT'), (1, 'AWS_KINESIS_DECODER')], default=0, null=True)),
                ('transformer_type', models.IntegerField(blank=True, choices=[(0, 'UNKNOWN_TT'), (2, 'SEGMENT_DFAULT_TRANSFORMER'), (3, 'AMPLITUDE_DEFAULT_TRANSFORMER'),], default=0, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.account')),
            ],
            options={
                'unique_together': {('account', 'decoder_type', 'transformer_type')},
            },
        ),
    ]
