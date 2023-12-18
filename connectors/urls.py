from django.urls import path

from . import views as connector_views

urlpatterns = [
    path('request', connector_views.connectors_request),
    path('create', connector_views.connectors_create),
    path('get_keys', connector_views.get_keys),
    path('delete_keys', connector_views.delete_keys),
    path('save_keys', connector_views.save_keys),
    path('transformer_mapping_create', connector_views.transformer_mapping_create),

    # event processing
    path('event_processing_filters/get', connector_views.event_processing_filters_get),
    path('event_processing_filters/create', connector_views.event_processing_filters_create),
    path('event_processing_filters/update', connector_views.event_processing_filters_update),
    path('event_processing_filters/apply', connector_views.event_processing_filters_apply),

    path('event_processing_parsers/get', connector_views.event_processing_parsers_get),
    path('event_processing_parsers/create', connector_views.event_processing_parsers_create),
    path('event_processing_parsers/update', connector_views.event_processing_parsers_update),
    path('event_processing_parsers/apply_parser', connector_views.event_processing_parsers_apply_parser),
    path('event_processing_parsers/apply_drd_event_definition_rule',
         connector_views.event_processing_parsers_apply_drd_event_definition_rule),

    path('event_processing_filters_parsers/create', connector_views.event_processing_filters_parsers_create),
]