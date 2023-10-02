from django.contrib import admin

from connectors.models import ConnectorRequest, TransformerMapping, Connector, ConnectorKey


@admin.register(ConnectorRequest)
class ConnectorRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "created_at",
        "connector_type",
    ]
    list_filter = ("account", "connector_type",)


@admin.register(ConnectorKey)
class ConnectorKeyAdmin(admin.ModelAdmin):
    list_display = [
        "account",
        "connector",
        "key_type",
        "created_at",
        "is_active",
    ]


@admin.register(Connector)
class ConnectorAdmin(admin.ModelAdmin):
    list_display = [
        "account",
        "connector_type",
        "created_at",
        "is_active",
    ]

@admin.register(TransformerMapping)
class TransformerMappingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "decoder_type",
        "transformer_type",
        "is_active",
    ]
    list_filter = ("account", "transformer_type", "decoder_type", "is_active")
