# Generated by Django 4.1.4 on 2023-09-11 09:33

import clickhouse_backend.models
from django.db import migrations, models
import django.db.models.deletion
import prototype.fields


class Migration(migrations.Migration):

    dependencies = [
        ("event", "0025_events_entitytrigger_rule_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="alert",
            name="entity_trigger",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="event.entitytrigger",
            ),
        ),
        migrations.AlterField(
            model_name="alert",
            name="trigger",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="event.trigger",
            ),
        ),
    ]
