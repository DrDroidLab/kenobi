# Generated by Django 4.1.4 on 2023-03-22 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0011_trigger_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='trigger',
            name='generated_config',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
