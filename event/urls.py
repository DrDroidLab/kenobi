from django.urls import path

from . import views

urlpatterns = [
    path('ingest/events/v1', views.ingest_events_v1),
    path('ingest/events/v2', views.ingest_events_v2),
    path('ingest/events/aws_kinesis', views.aws_kinesis_ingest_events),
    path('ingest/events/aws_kinesis/v2', views.aws_kinesis_ingest_events_v2),
    path('ingest/events/collector', views.ingest_events_collector),

    path('api/search/options', views.global_search_options_get),
    path('api/events', views.events_get),
    path('api/search/options/events', views.event_search_options_get),
    path('api/events/search', views.events_search),
    path('api/events/search/save', views.save_events_search),
    path('api/events/search/v2', views.events_search_v2),
    path('api/events/export', views.events_export),
    path('api/event_keys/search', views.event_keys_search),
    path('api/event_types/summary', views.event_types_summary),
    path('api/event_types/definition', views.event_types_definition),
    path('api/monitors/create', views.monitors_create),
    path('api/monitors/update', views.monitors_update),
    path('api/monitors', views.monitors_get),
    path('api/monitors/options', views.monitors_option),
    path('api/monitors/definition', views.monitors_definition),
    path('api/monitors/transactions', views.monitors_transactions_get),
    path('api/monitors/transactions/events', views.monitors_transactions_events_get),
    path('api/monitors/transactions/details', views.monitors_transactions_details),
    path('api/search/options/monitors/transactions', views.monitor_transaction_search_options_get),
    path('api/search/options/monitors/transactions/v2', views.monitor_transaction_search_options_get_v2),
    path('api/monitors/transactions/search', views.monitors_transactions_search),
    path('api/monitors/transactions/export', views.monitors_transactions_export),
    path('api/monitors/transactions/export/v2', views.monitors_transactions_export_v2),
    path('api/monitors/transactions/search/v2', views.monitors_transactions_search_v2),
    path('api/monitors/transactions/search/save', views.save_monitor_transactions_search),
    path('api/monitors/triggers', views.monitors_triggers_get),
    path('api/monitors/triggers/options', views.monitors_triggers_options),
    path('api/monitors/triggers/create', views.monitors_triggers_create),
    path('api/monitors/triggers/update', views.monitors_triggers_update),

    path('api/metrics/options', views.metrics_options),
    path('api/metrics', views.metrics),

    path('api/panels_v1', views.panels_v1_get),
    path('api/panels_v1/create_or_update', views.panels_v1_create_or_update),
    path('api/panels_v1/delete', views.panels_v1_delete),

    path('api/dashboard_v1', views.dashboards_v1_get),
    path('api/dashboard_v1/create_or_update', views.dashboard_v1_create_or_update),
    path('api/dashboard_v1/delete', views.dashboards_v1_delete),

    path('api/alerts/summary', views.alerts_summary_get),
    path('api/alerts/details', views.alerts_details_get),
    path('api/alerts/monitor_transactions', views.alerts_monitor_transactions_get),

    path('api/notifications_get', views.notifications_get),
    path('api/notifications_create', views.notifications_create),

    path('api/entity/create/options', views.entity_options_get),
    path('api/entity/create', views.entity_create),
    path('api/entity/update', views.entity_update),
    path('api/entity', views.entity_summary_get),
    path('api/entity/details', views.entity_detail_get),
    path('api/entity/instances', views.entity_instances_summary_get),
    path('api/entity/instances/details', views.entity_instances_details_get),
    path('api/entity/instances/timeline', views.entity_instances_timeline_get),
    path('api/search/options/entity/instances', views.entity_instance_search_options_get),
    path('api/search/options/entity/instances/v2', views.entity_instance_search_options_get_v2),
    path('api/entity/instances/search', views.entity_instances_search),

    path('api/entities/triggers/get', views.entity_triggers_get),
    path('api/entities/triggers/options', views.entity_triggers_options),
    path('api/entities/triggers/create', views.entity_triggers_create),
    path('api/entities/triggers/update', views.entity_triggers_update),
    path('api/entities/triggers/inactivate', views.entity_triggers_inactivate),

    path('api/entity/workflow', views.entity_workflow_get),
    path('api/entity/build_workflow', views.workflow_builder),
    path('api/entity/node_metrics_timeseries', views.workflow_node_metrics_timeseries),

    path('api/funnel/v2', views.funnel_get_v2),
    path('api/funnel/drop_off_distribution/v2', views.funnel_drop_off_distribution_get_v2),
    path('api/funnel/drop_off', views.funnel_drop_off_get),

    path('api/funnel/v3', views.funnel_get_v3),

    # Funnel Revamp
    path('api/entity_funnels/view', views.funnel_get_v2),
    path('api/entity_funnels/create', views.entity_funnel_create),
    path('api/entity_funnels/get', views.entity_funnel_get),
    path('api/entity_funnels/update', views.entity_funnel_update),
    path('api/entity_funnels/drop_off_distribution', views.entity_funnel_drop_off_distribution_get),
    path('api/entity_funnels/drop_off_distribution/download', views.entity_funnel_drop_off_distribution_download),
]
