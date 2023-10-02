from django.urls import path

from . import views as connector_views

urlpatterns = [
    path('request', connector_views.connectors_request),
    path('create', connector_views.connectors_create),
    path('get_keys', connector_views.get_keys),
    path('delete_keys', connector_views.delete_keys),
    path('save_keys', connector_views.save_keys),
    path('transformer_mapping_create', connector_views.transformer_mapping_create),
]
