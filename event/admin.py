from django.contrib import admin

from event.models import EventType, EventKey, Event, Monitor, MonitorTransaction, MonitorTransactionEventMapping, \
    Notification, Panel, Trigger, Alert, TriggerNotificationConfigMapping, AlertMonitorTransactionMapping, \
    MonitorTransactionStats, Entity, EntityInstance, EntityInstanceEventMapping, EntityEventKeyMapping, EntityTrigger, \
    EntityMonitorMapping


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "account",
        "created_at",
        "event_sources",
    ]
    list_filter = ("account",)


@admin.register(EventKey)
class EventKeyAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "event_type",
        "account",
        "created_at",
        "type",
    ]
    list_filter = ("account", "type")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "event_type",
        "processed_kvs",
        "created_at",
        "timestamp",
        "event_source",
    ]
    list_filter = ("event_type", "account",)


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "account",
        "primary_key",
        "secondary_key",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ("account", "primary_key", "secondary_key",)


class MonitorTransactionEventMappingAdminInline(admin.TabularInline):
    model = MonitorTransactionEventMapping
    raw_id_fields = ("monitor_transaction", "event", "account")


class MonitorTransactionStatsAdminInline(admin.TabularInline):
    model = MonitorTransactionStats
    raw_id_fields = ("monitor_transaction", "account")


@admin.register(EntityTrigger)
class EntityTriggerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "name",
        "is_active",
        "entity",
        "type",
        "rule_type",
        "created_at"
    ]
    list_filter = ("entity", "type", "rule_type", "is_active")


@admin.register(MonitorTransaction)
class MonitorTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "monitor",
        "transaction",
        "created_at",
        "type",
    ]
    inlines = [MonitorTransactionEventMappingAdminInline, MonitorTransactionStatsAdminInline]
    list_filter = ("account", "monitor", "type",)
    list_per_page = 10


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "channel",
        "config",
    ]
    list_filter = ("account", "channel")


class TriggerNotificationMappingAdminInline(admin.TabularInline):
    model = TriggerNotificationConfigMapping


@admin.register(TriggerNotificationConfigMapping)
class TriggerNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "trigger",
        "notification",
        "created_at",
    ]
    list_filter = ("account", "trigger", "notification",)


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "name",
        "created_at",
        "updated_at",
    ]
    list_filter = ("account",)


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "name",
        "monitor",
        "type",
        "priority",
        "is_active",
        "created_at",
        "updated_at",
    ]
    inlines = [TriggerNotificationMappingAdminInline]
    list_filter = ("account",)


class AlertMonitorTransactionMappingAdminInline(admin.TabularInline):
    model = AlertMonitorTransactionMapping


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "trigger",
        "triggered_at",
    ]
    inlines = [AlertMonitorTransactionMappingAdminInline]
    list_filter = ("account", 'trigger')


@admin.register(AlertMonitorTransactionMapping)
class AlertMonitorTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "alert",
        "monitor_transaction",
        "type",
        "created_at",
    ]
    list_filter = ("account", "alert", "monitor_transaction",)


class EntityEventKeyMappingAdminInline(admin.TabularInline):
    model = EntityEventKeyMapping
    raw_id_fields = ("entity", "event_key",)


class EntityMonitorMappingAdminInline(admin.TabularInline):
    model = EntityMonitorMapping
    raw_id_fields = ("entity", "monitor",)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "name",
        "type",
        "is_active",
        "is_generated",
        "created_at",
    ]
    inlines = [EntityEventKeyMappingAdminInline, EntityMonitorMappingAdminInline]
    list_filter = ("account", "type", "is_active", "is_generated",)


@admin.register(EntityInstance)
class EntityInstanceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "entity",
        "created_at",
    ]
    list_filter = ("account",)


@admin.register(EntityMonitorMapping)
class EntityMonitorMappingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "entity",
        "monitor",
        "is_active",
        "is_generated",
        "created_at"
    ]
    list_filter = ("account", "is_active", "is_generated", "entity", "monitor")
