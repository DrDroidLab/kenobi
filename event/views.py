import json
import logging
import traceback
import uuid
from datetime import timedelta, datetime
from typing import Union
from collections import defaultdict
import csv

from django.db import transaction as dj_transaction
from django.db.models import F, Avg, FloatField, OuterRef, Subquery, Count
from django.db.models import QuerySet
from django.db.models.functions import Cast
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.protobuf.wrappers_pb2 import BoolValue, UInt64Value, StringValue, DoubleValue
from rest_framework.decorators import api_view, authentication_classes

from accounts.authentication import AccountApiTokenAuthentication
from accounts.models import get_request_account, Account, get_request_user, User
from accounts.utils import do_process_events, AccountDailyEventQuotaReached, get_account_quota_error_message
from connectors.integrations.datadog import DatadogConnector
from connectors.integrations.newrelic import NewRelicConnector
from connectors.models import TransformerMapping
from connectors.transformers.transformer import transformer_facade
from event.base.op import OP_DESCRIPTIONS, OP_MAPPINGS, LITERAL_TYPE_DESCRIPTIONS
from event.cache import GLOBAL_PANEL_CACHE, GLOBAL_DASHBOARD_CACHE, GLOBAL_EVENT_QUERY_SEARCH_REQUEST_CACHE, \
    GLOBAL_MONITOR_TRANSACTION_QUERY_SEARCH_REQUEST_CACHE, GLOBAL_EXPORT_CONTEXT_CACHE
from event.engine.fuzzy_match_engine import event_type_fuzzy_match_engine, monitor_fuzzy_match_engine, \
    entity_fuzzy_match_engine
from event.engine.metric_engine import process_metric_expressions, get_metric_options, get_default_metric_expression, \
    process_workflow_metric_expression
from event.engine.query_engine import global_event_search_engine, global_event_search_clickhouse_engine, \
    monitor_transaction_search_engine, \
    entity_instance_search_engine
from event.entity_funnels.clickhouse_funnels_crud import entity_funnels_get_clickhouse_events, \
    entity_funnels_get_clickhouse_drop_off_distribution, entity_funnels_get_clickhouse_drop_off_distribution_download, \
    get_funnel_panel_data
from event.entity_funnels.entity_funnels_crud import entity_funnels_create, entity_funnels_get, \
    EntityFunnelCrudNotFoundException, entity_funnels_drop_off_get, entity_funnels_drop_off_download
from event.models import is_transactional_key_type, Notification, Alert, is_filterable_key_type, \
    TRANSACTIONAL_KEY_TYPES, Entity, EntityEventKeyMapping, Trigger, MonitorTransactionStats, \
    MonitorTransactionEventMapping, EventKey, EntityTrigger, EntityTriggerNotificationConfigMapping
from event.monitors_crud import create_monitors, update_monitors
from event.monitors_triggers_crud import create_monitor_triggers
from event.notification.notification_facade import notification_client
from event.notification.notifications_crud import create_db_notifications
from event.processors.process_events_payload import process_account_events_payload
from event.tasks import export_task
from event.triggers.trigger_processor import get_default_trigger_options
from event.update_processor import entity_update_processor, monitor_trigger_update_processor, \
    entity_funnel_update_processor
from event.workflows.builder import WorkflowBuilder
from event.workflows.graph import Graph, NewGraph
from protos.event.alert_pb2 import AlertDetail
from protos.event.api_pb2 import *
from protos.event.base_pb2 import TimeRange, Page, EventKey as EventKeyProto, Event as EventProto, EventTypePartial, \
    EventTypeStats, EventTypeSummary, Context
from protos.event.engine_options_pb2 import GlobalQueryOptions
from protos.event.entity_pb2 import UpdateEntityFunnelOp, Entity as EntityProto
from protos.event.timeline_pb2 import EntityInstanceTimelineRecord
from protos.event.monitor_pb2 import MonitorPartial, MonitorTransactionPartial, MonitorStats, \
    MonitorTransaction as MonitorTransactionProto
from protos.event.notification_pb2 import NotificationConfig
from protos.event.options_pb2 import MonitorTriggerOptions
from protos.event.options_pb2 import TriggerOption, MonitorOptions, NotificationOption, EntityOptions
from protos.event.panel_pb2 import PanelV1, DashboardV1, ComplexTableData, PanelData
from protos.event.query_base_pb2 import QueryRequest
from protos.event.schema_pb2 import IngestionEventPayloadRequest, IngestionEventPayloadResponse, IngestionEventPayload, \
    KeyValue, IngestionEvent, Value as ValueProto, AWSKinesisIngestionStreamPayloadRequest, \
    AWSKinesisIngestionStreamPayloadResponse, \
    AWSKinesisEventPayload
from protos.event.trigger_pb2 import Trigger as TriggerProto, MonitorTriggerNotificationDetail, \
    EntityTriggerNotificationDetail
from prototype.aggregates import Percentile
from prototype.db.decorator import use_read_replica
from prototype.entity_utils import annotate_entity_instance_stats, annotate_entity_timeline
from prototype.threadlocal import get_current_request
from prototype.utils.decorators import account_data_api, web_api, api_auth_check, aws_kinesis_data_api, \
    ProtoJsonResponse
from prototype.utils.meta import get_meta
from prototype.utils.queryset import filter_time_range, filter_page
from prototype.utils.timerange import to_dtr, DateTimeRange, to_tr, filter_dtr
from prototype.utils.utils import current_milli_time
from utils.proto_utils import proto_to_dict, dict_to_proto

from event.clickhouse.models import Events

EVENT_TIME_FIELD = 'timestamp'

logger = logging.getLogger(__name__)


def infer_value_type(v):
    if isinstance(v, str):
        return EventKeyProto.KeyType.STRING, ValueProto(string_value=v)
    elif isinstance(v, bool):
        return EventKeyProto.KeyType.BOOLEAN, ValueProto(bool_value=v)
    elif isinstance(v, int):
        return EventKeyProto.KeyType.LONG, ValueProto(int_value=v)
    elif isinstance(v, float):
        return EventKeyProto.KeyType.DOUBLE, ValueProto(double_value=v)
    return EventKeyProto.KeyType.UNKNOWN, None


def transform_event_json(event_json: dict):
    event_name: str = event_json.get('name', '')
    if not event_json:
        return None
    payload = event_json.get('payload', None)
    if not isinstance(payload, dict):
        return None

    timestamp_in_ms = event_json.get('timestamp', current_milli_time())

    kvlist = []
    for key, value in payload.items():
        _, proto_value = infer_value_type(value)
        if not proto_value:
            continue
        kvlist.append(KeyValue(key=key, value=proto_value))

    return IngestionEvent(name=event_name, kvs=kvlist, timestamp=timestamp_in_ms)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([AccountApiTokenAuthentication])
@api_auth_check
def ingest_events_v1(request: HttpRequest):
    # Process the events and metadata and put it into db
    body = request.body
    parsed_body = json.loads(body)
    event = transform_event_json(parsed_body)
    if not event:
        return JsonResponse({'count': 0}, status=200)
    account: Account = get_request_account()

    event_count = 1
    try:
        do_process_events(account.id, event_count)
    except AccountDailyEventQuotaReached as e:
        return JsonResponse({'count': 0, 'errorMessage': get_account_quota_error_message()}, status=200)

    count = process_account_events_payload(account, IngestionEventPayload(events=[event]), EventProto.EventSource.API)
    return JsonResponse({'count': count}, status=200)


@account_data_api(IngestionEventPayloadRequest)
def ingest_events_v2(request_message: IngestionEventPayloadRequest) -> Union[
    IngestionEventPayloadResponse, HttpResponse]:
    # Process the events and metadata and put it into db
    account: Account = get_request_account()

    data: IngestionEventPayload = request_message.data
    if not data:
        return IngestionEventPayloadResponse(count=0)

    event_count = len(data.events)
    try:
        do_process_events(account.id, event_count)
    except AccountDailyEventQuotaReached as e:
        return IngestionEventPayloadResponse(count=0, errorMessage=get_account_quota_error_message())

    count = process_account_events_payload(account, data)
    return JsonResponse({'count': count}, status=200)


@aws_kinesis_data_api(AWSKinesisIngestionStreamPayloadRequest)
def aws_kinesis_ingest_events(request_message: AWSKinesisIngestionStreamPayloadRequest) -> Union[
    AWSKinesisIngestionStreamPayloadResponse, HttpResponse]:
    # Process the kinesis delivery stream of segment events and put it into db

    account: Account = get_request_account()

    request_headers = get_current_request().headers
    common_attributes_headers = request_headers.get('X-Amz-Firehose-Common-Attributes', None)
    if not common_attributes_headers:
        return JsonResponse({'error': 'Missing Common Attributes Header'}, status=400,
                            content_type='application/json')

    common_attributes = json.loads(common_attributes_headers).get('commonAttributes')
    if not common_attributes:
        return JsonResponse({'error': 'Missing Common Attributes'}, status=400,
                            content_type='application/json')

    source = EventProto.EventSource.Value(common_attributes.get('source', 'UNKNOWN'))
    transformer_id = int(common_attributes.get('transformer_id', None))
    if not transformer_id:
        return JsonResponse({'error': 'Invalid transformer id'}, status=400,
                            content_type='application/json')

    transformer_mapping: TransformerMapping = account.transformermapping_set.get(id=transformer_id)
    if not transformer_mapping:
        print(
            f"No transformer mapping found for AWS Kinesis Ingestion for account id: {account.id} and transformer id: {transformer_id}")

    request_id: str = request_message.requestId
    records: [AWSKinesisEventPayload] = request_message.records
    timestamp = request_message.timestamp
    transformed_event_list = []
    for record in records:
        try:
            events = transformer_facade.transform(transformer_mapping, record)
            if not events:
                continue
            for event in events:
                transformed_event = transform_event_json(event)
                transformed_event_list.append(transformed_event)
        except Exception as ex:
            print(
                f"Transformer Error in AWS Kinesis Ingestion: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    count = 0
    if transformed_event_list:
        count = process_account_events_payload(account, IngestionEventPayload(events=transformed_event_list), source)

    print("Processed: {} AWS Kinesis Ingestion Events for account id: {}".format(count, account.id))
    return JsonResponse({'requestId': request_id, 'timestamp': timestamp}, status=200,
                        content_type='application/json')


@web_api(GetEventsRequest)
@use_read_replica
def events_get(request_message: GetEventsRequest) -> Union[GetEventsResponse, HttpResponse]:
    # Process the events and metadata and put it into db
    account: Account = get_request_account()
    meta: Meta = request_message.meta
    tr: TimeRange = meta.time_range
    page: Page = meta.page

    qs = Events.objects.filter(account_id=account.id)

    if request_message.event_type_ids:
        qs = qs.filter(event_type_id__in=request_message.event_type_ids)

    qs = filter_time_range(qs, tr, 'timestamp')
    total_count = qs.count()
    qs = qs.order_by('-timestamp')
    qs = filter_page(qs, page)

    event_protos = [e.proto for e in qs]

    return GetEventsResponse(meta=get_meta(tr=tr, page=page, total_count=total_count), events=event_protos)


@web_api(GetEventSearchQueryRequest)
@use_read_replica
def events_search(request_message: GetEventSearchQueryRequest) -> Union[GetEventSearchQueryResponse, HttpResponse]:
    # Search events given a search request
    account: Account = get_request_account()
    page = request_message.meta.page
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    query_request = request_message.query_request

    generated_search_context_id = None
    if request_message.save_query.value:
        generated_search_context_id = uuid.uuid4().hex
        query_request_dict = proto_to_dict(query_request)
        GLOBAL_EVENT_QUERY_SEARCH_REQUEST_CACHE.create_or_update(account.id, generated_search_context_id,
                                                                 query_request_dict, None)

    qs = Events.objects.all()
    qs = filter_dtr(qs, dtr, 'timestamp')
    qs = qs.filter(account_id=account.id)
    qs = global_event_search_clickhouse_engine.process_query(qs, query_request)
    total_count = qs.count()

    qs = filter_page(qs, page)
    event_protos = [e.proto for e in qs]

    return GetEventSearchQueryResponse(meta=get_meta(total_count=total_count, tr=dtr.to_tr(), page=page),
                                       events=event_protos, query_context_id=generated_search_context_id)


@web_api(SaveEventSearchQueryRequest)
@use_read_replica
def save_events_search(request_message: SaveEventSearchQueryRequest) -> Union[
    SaveEventSearchQueryResponse, HttpResponse]:
    # Save events search context
    account: Account = get_request_account()

    generated_search_context_id = uuid.uuid4().hex
    query_request_dict = proto_to_dict(request_message.query_request)
    GLOBAL_EVENT_QUERY_SEARCH_REQUEST_CACHE.create_or_update(account.id, generated_search_context_id,
                                                             query_request_dict, None)

    return SaveEventSearchQueryResponse(meta=get_meta(), query_context_id=generated_search_context_id)


@web_api(GetEventSearchQueryRequest)
@use_read_replica
def events_search_v2(request_message: GetEventSearchQueryRequest) -> Union[GetEventSearchQueryResponse, HttpResponse]:
    # Search events given a search request
    account: Account = get_request_account()
    page = request_message.meta.page
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    query_request = request_message.query_request

    generated_search_context_id = None
    if request_message.save_query.value:
        generated_search_context_id = uuid.uuid4().hex
        query_request_dict = proto_to_dict(request_message.query_request)
        GLOBAL_EVENT_QUERY_SEARCH_REQUEST_CACHE.create_or_update(account.id, generated_search_context_id,
                                                                 query_request_dict, None)

    qs = Events.objects.all()
    qs = filter_dtr(qs, dtr, 'timestamp')
    qs = qs.filter(account_id=account.id)
    qs = global_event_search_clickhouse_engine.process_query(qs, query_request)
    total_count = qs.count()

    qs = global_event_search_clickhouse_engine.process_ordering(qs, query_request)

    qs = filter_page(qs, page)
    event_protos = [e.proto for e in qs]

    return GetEventSearchQueryResponse(meta=get_meta(total_count=total_count, tr=dtr.to_tr(), page=page),
                                       events=event_protos, query_context_id=generated_search_context_id)


@web_api(GetEventExportQueryRequest)
@use_read_replica
def events_export(request_message: GetEventExportQueryRequest) -> Union[
    GetEventExportQueryResponse, HttpResponse]:
    # Export events given a search request

    account: Account = get_request_account()
    user: User = get_request_user()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    query_request = request_message.query_request

    export_id = uuid.uuid4().hex
    if GLOBAL_EXPORT_CONTEXT_CACHE.get(account.id, Context.EVENT, user.email):
        export_id = GLOBAL_EXPORT_CONTEXT_CACHE.get(account.id, Context.EVENT, user.email)
    else:
        qs = Events.objects.all()
        qs = filter_dtr(qs, dtr, 'timestamp')
        qs = qs.filter(account_id=account.id)
        qs = global_event_search_clickhouse_engine.process_query(qs, query_request)
        if qs.count() > 10000:
            return GetEventExportQueryResponse(meta=get_meta(), success=BoolValue(value=False),
                                               message=Message(title="Event Export Failure",
                                                               description="Export size too large"))
        else:
            GLOBAL_EXPORT_CONTEXT_CACHE.create_or_update(account.id, Context.EVENT, user.email, export_id)
            export_task_request, message = export_task(account.id, Context.EVENT, user.email,
                                                       proto_to_dict(request_message))

            if not export_task_request:
                return GetEventExportQueryResponse(meta=get_meta(), success=BoolValue(value=False),
                                                   message=Message(title="Event Export Failure",
                                                                   description=message))

    return GetEventExportQueryResponse(meta=get_meta(), success=BoolValue(value=True), export_context_id=export_id)


@web_api(GetEventKeysSearchRequest)
@use_read_replica
def event_keys_search(request_message: GetEventKeysSearchRequest) -> Union[
    GetEventKeysSearchResponse, HttpResponse]:
    account: Account = get_request_account()
    event_key_ids = request_message.event_key_ids

    event_keys = EventKey.objects.filter(account_id=account.id, id__in=event_key_ids).values_list('name', flat=True)
    similar_event_keys = EventKey.objects.filter(account_id=account.id, name__in=event_keys).exclude(
        id__in=event_key_ids)

    similar_event_keys_protos = [e.proto for e in similar_event_keys]
    return GetEventKeysSearchResponse(event_keys=similar_event_keys_protos)


@web_api(GetEventTypeSummaryRequest)
@use_read_replica
def event_types_summary(request_message: GetEventTypeSummaryRequest) -> Union[
    GetEventTypeSummaryResponse, HttpResponse]:
    account: Account = get_request_account()
    meta: Meta = request_message.meta
    tr: TimeRange = meta.time_range
    page: Page = meta.page

    is_event_type_page = False

    qs: QuerySet = account.eventtype_set.all()
    if request_message.fuzzy_search_request.pattern:
        qs: QuerySet = event_type_fuzzy_match_engine.match_pattern(account,
                                                                   request_message.fuzzy_search_request.pattern)
    if request_message.event_type_ids:
        qs = qs.filter(id__in=request_message.event_type_ids)
        if len(request_message.event_type_ids) == 1:
            is_event_type_page = True

    total_count = qs.count()
    qs = filter_page(qs, page)

    summaries = []

    if is_event_type_page:
        event_type_info = [EventTypePartial(id=event_type.id, name=str(event_type.name)) for event_type in qs][0]
        summaries.append(EventTypeSummary(event_type=event_type_info, stats=None))
    else:
        monitor_and_keys_summaries = [event_type.monitor_and_keys_summary() for event_type in qs]

        event_type_ids = [event_type.id for event_type in qs]
        e_qs = Events.objects.filter(account_id=account.id)
        e_qs = filter_dtr(e_qs, tr, 'timestamp')
        e_qs = e_qs.filter(event_type_id__in=event_type_ids)
        e_qs = e_qs.values('event_type_id').annotate(count=Count('id'))

        event_type_counts = list(e_qs)
        event_type_counts_map = {e['event_type_id']: e['count'] for e in event_type_counts}

        for summary in monitor_and_keys_summaries:
            event_count = event_type_counts_map.get(summary[0].id, 0)
            stats = EventTypeStats(keys_count=UInt64Value(value=summary[1].get('keys_count')),
                                   event_count=UInt64Value(value=event_count),
                                   monitor_count=UInt64Value(value=summary[1].get('monitor_count')))
            summaries.append(EventTypeSummary(event_type=summary[0], stats=stats))

    return GetEventTypeSummaryResponse(meta=get_meta(tr=tr, page=page, total_count=total_count),
                                       event_type_summary=summaries)


@web_api(GetEventTypeDefinitionRequest)
@use_read_replica
def event_types_definition(request_message: GetEventTypeDefinitionRequest) -> Union[
    GetEventTypeDefinitionResponse, HttpResponse]:
    account: Account = get_request_account()
    meta: Meta = request_message.meta
    tr: TimeRange = meta.time_range
    page: Page = meta.page

    qs: QuerySet = account.eventtype_set.all()
    if request_message.event_type_ids:
        qs = qs.filter(id__in=request_message.event_type_ids)

    total_count = qs.count()
    qs = filter_page(qs, page)

    definitions = [event_type.definition(tr) for event_type in qs]

    return GetEventTypeDefinitionResponse(meta=get_meta(tr=tr, page=page, total_count=total_count),
                                          event_type_definitions=definitions)


@web_api(CreateOrUpdateMonitorRequest)
def monitors_create(request_message: CreateOrUpdateMonitorRequest) -> Union[
    CreateOrUpdateMonitorResponse, HttpResponse]:
    account: Account = get_request_account()

    monitor_name: str = request_message.name
    primary_event_key_id = request_message.primary_event_key_id
    secondary_event_key_id = request_message.secondary_event_key_id

    db_monitor, created, error = create_monitors(account, monitor_name, primary_event_key_id, secondary_event_key_id)
    if error and not created:
        if db_monitor:
            return CreateOrUpdateMonitorResponse(success=BoolValue(value=False),
                                                 message=Message(title="Monitor Creation Failure",
                                                                 description=error),
                                                 monitor=db_monitor.proto_partial)
        else:
            return CreateOrUpdateMonitorResponse(success=BoolValue(value=False),
                                                 message=Message(title="Monitor Creation Failure",
                                                                 description=error))
    return CreateOrUpdateMonitorResponse(success=BoolValue(value=True), monitor=db_monitor.proto_partial)


@web_api(CreateOrUpdateMonitorRequest)
def monitors_update(request_message: CreateOrUpdateMonitorRequest) -> Union[
    CreateOrUpdateMonitorResponse, HttpResponse]:
    account: Account = get_request_account()

    return update_monitors(account, request_message)


@web_api(GetMonitorDefinitionRequest)
@use_read_replica
def monitors_definition(request_message: GetMonitorDefinitionRequest) -> Union[
    GetMonitorDefinitionResponse, HttpResponse]:
    account: Account = get_request_account()
    meta: Meta = request_message.meta
    tr: TimeRange = meta.time_range
    page: Page = meta.page

    qs: QuerySet = account.monitor_set.all()
    if request_message.monitor_ids:
        qs = qs.filter(id__in=request_message.monitor_ids)

    total_count = qs.count()
    qs = qs.order_by('-created_at')
    qs = filter_page(qs, page)

    qs = qs.select_related('primary_key', 'primary_key__event_type', 'secondary_key', 'secondary_key__event_type')

    definitions = [monitor.definition(tr) for monitor in qs]

    return GetMonitorDefinitionResponse(meta=get_meta(tr=tr, page=page, total_count=total_count),
                                        monitor_definitions=definitions)


@web_api(GetMonitorRequest)
@use_read_replica
def monitors_get(request_message: GetMonitorRequest) -> Union[GetMonitorResponse, HttpResponse]:
    account: Account = get_request_account()
    meta: Meta = request_message.meta
    tr: TimeRange = meta.time_range
    show_inactive = meta.show_inactive
    page: Page = meta.page

    qs: QuerySet = account.monitor_set.filter(is_generated=False)
    if request_message.fuzzy_search_request.pattern:
        qs: QuerySet = monitor_fuzzy_match_engine.match_pattern(account, request_message.fuzzy_search_request.pattern)

    if request_message.monitor_ids:
        qs = qs.filter(id__in=request_message.monitor_ids)
    elif not show_inactive or not show_inactive.value:
        qs = qs.filter(is_active=True)

    total_count = qs.count()
    qs = qs.order_by('-created_at')
    qs = filter_page(qs, page)

    qs = qs.select_related('primary_key', 'primary_key__event_type', 'secondary_key', 'secondary_key__event_type')

    monitors = [monitor.proto for monitor in qs]

    return GetMonitorResponse(meta=get_meta(page=page, total_count=total_count, show_inactive=show_inactive),
                              monitors=monitors)


@web_api(GetMonitorOptionsRequest)
@use_read_replica
def monitors_option(request_message: GetMonitorOptionsRequest) -> Union[GetMonitorOptionsResponse, HttpResponse]:
    account: Account = get_request_account()

    qs: QuerySet = account.eventkey_set.filter()
    qs = qs.prefetch_related('event_type')

    total_count = qs.count()

    event_key_options = [ek.proto for ek in qs if is_transactional_key_type(ek.type)]

    return GetMonitorOptionsResponse(
        meta=get_meta(total_count=total_count),
        monitor_options=MonitorOptions(event_key_options=event_key_options)
    )


@web_api(GetMonitorTransactionsRequest)
@use_read_replica
def monitors_transactions_get(request_message: GetMonitorTransactionsRequest) -> Union[
    GetMonitorTransactionsResponse, HttpResponse]:
    account: Account = get_request_account()
    meta: Meta = request_message.meta
    tr: TimeRange = meta.time_range
    page: Page = meta.page

    monitor_id = request_message.monitor_id

    qs: QuerySet = account.monitortransaction_set.all()

    if monitor_id:
        qs = qs.filter(monitor_id=monitor_id)

    if request_message.params:
        params = request_message.params
        transaction_ids = params.transaction_ids
        transactions = params.transactions
        transaction_status = params.transaction_status
        if transaction_ids:
            qs = qs.filter(id__in=transaction_ids)
        elif transactions:
            qs = qs.filter(trasaction__in=transactions)
        elif transaction_status:
            qs = qs.filter(type=transaction_status)

    qs = filter_time_range(qs, tr, 'updated_at')
    total_count = qs.count()
    qs = qs.order_by('-updated_at')
    qs = filter_page(qs, page)

    qs = qs.prefetch_related('monitor')

    monitor_transactions = [monitor_transaction.proto for monitor_transaction in qs]

    qs: QuerySet = account.alertmonitortransactionmapping_set.all()
    qs = qs.prefetch_related('alert', 'alert__trigger')
    qs = qs.filter(monitor_transaction_id__in=transaction_ids)
    alert_monitor_transaction_mappings = [amtm.miniproto for amtm in qs]

    return GetMonitorTransactionsResponse(meta=get_meta(tr=tr, page=page, total_count=total_count),
                                          monitor_transactions=monitor_transactions,
                                          alerts=alert_monitor_transaction_mappings)


@web_api(GetMonitorTransactionEventsRequest)
@use_read_replica
def monitors_transactions_events_get(request_message: GetMonitorTransactionEventsRequest) -> Union[
    GetMonitorTransactionEventsResponse, HttpResponse]:
    account: Account = get_request_account()
    meta: Meta = request_message.meta
    tr: TimeRange = meta.time_range
    page: Page = meta.page

    transaction_id = request_message.transaction_id

    if not transaction_id:
        return GetMonitorTransactionEventsResponse(meta=get_meta(tr=tr, page=page))

    qs: QuerySet = account.monitortransactioneventmapping_set.all()

    qs = qs.filter(monitor_transaction_id=transaction_id)
    events = [mte.event.proto for mte in qs]

    return GetMonitorTransactionEventsResponse(meta=get_meta(tr=tr, page=page),
                                               events=events)


@web_api(GetMonitorTransactionDetailsRequest)
@use_read_replica
def monitors_transactions_details(request_message: GetMonitorTransactionDetailsRequest) -> Union[
    GetMonitorTransactionDetailsResponse, HttpResponse]:
    account: Account = get_request_account()

    transaction_id = request_message.transaction_id

    if not transaction_id:
        return GetMonitorTransactionDetailsResponse(meta=get_meta())

    qs: QuerySet = account.monitortransactionstats_set.all()

    qs = qs.filter(monitor_transaction_id=transaction_id)
    qs = qs.select_related('monitor_transaction__monitor')
    details = [mte.proto for mte in qs]

    return GetMonitorTransactionDetailsResponse(meta=get_meta(),
                                                monitor_transaction_details=details)


@web_api(GetMonitorsTransactionsSearchOptionsRequest)
@use_read_replica
def monitor_transaction_search_options_get(request_message: GetMonitorsTransactionsSearchOptionsRequest) -> Union[
    GetMonitorsTransactionsSearchOptionsResponse, HttpResponse]:
    account: Account = get_request_account()

    default_query = None
    saved_query_request_context_id = request_message.saved_query_request_context_id.string.value
    if saved_query_request_context_id:
        saved_context = GLOBAL_MONITOR_TRANSACTION_QUERY_SEARCH_REQUEST_CACHE.get(account.id,
                                                                                  saved_query_request_context_id)
        if saved_context:
            default_query = dict_to_proto(saved_context, QueryRequest)

    obj = monitor_transaction_search_engine.get_obj(account, request_message.id_literal)
    if not default_query:
        default_query = monitor_transaction_search_engine.get_default_query(account, obj)

    options = monitor_transaction_search_engine.get_search_options(account, obj)

    return GetMonitorsTransactionsSearchOptionsResponse(meta=get_meta(),
                                                        monitor_transaction_query_options=options,
                                                        default_query_request=default_query)


@web_api(GetMonitorsTransactionsSearchOptionsV2Request)
@use_read_replica
def monitor_transaction_search_options_get_v2(request_message: GetMonitorsTransactionsSearchOptionsV2Request) -> Union[
    GetMonitorsTransactionsSearchOptionsV2Response, HttpResponse]:
    account: Account = get_request_account()

    default_query = None
    saved_query_request_context_id = request_message.saved_query_request_context_id.string.value
    if saved_query_request_context_id:
        saved_context = GLOBAL_MONITOR_TRANSACTION_QUERY_SEARCH_REQUEST_CACHE.get(account.id,
                                                                                  saved_query_request_context_id)
        if saved_context:
            default_query = dict_to_proto(saved_context, QueryRequest)

    obj = monitor_transaction_search_engine.get_obj(account, request_message.id_literal)
    if not default_query:
        default_query = monitor_transaction_search_engine.get_default_query(account, obj)

    options = monitor_transaction_search_engine.get_search_options_v2(account, obj)

    return GetMonitorsTransactionsSearchOptionsV2Response(meta=get_meta(),
                                                          monitor_transaction_query_options=options,
                                                          default_query_request=default_query)


@web_api(GetMonitorsTransactionsSearchQueryRequest)
@use_read_replica
def monitors_transactions_search(request_message: GetMonitorsTransactionsSearchQueryRequest) -> Union[
    GetMonitorsTransactionsSearchQueryResponse, HttpResponse]:
    # Search monitor transactions given a search request
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    page = request_message.meta.page

    qs = account.monitortransaction_set.all()
    qs = filter_dtr(qs, dtr, 'created_at')
    qs = monitor_transaction_search_engine.process_query(qs, request_message.query_request)
    total_count = qs.count()
    monitor_transactions_finished = qs.filter(type=MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED)

    monitor_transactions_aggregates = monitor_transactions_finished.annotate(
        transaction_time=(Cast(F('monitortransactionstats__stats__transaction_time'), FloatField()))
    ).aggregate(
        p95=Percentile('transaction_time', percentile=0.95),
        p99=Percentile('transaction_time', percentile=0.99),
        avg_delay=Avg(F('transaction_time'))
    )

    avg_delay = monitor_transactions_aggregates.get('avg_delay')
    if not avg_delay:
        avg_delay = 0

    p95 = monitor_transactions_aggregates.get('p95', timedelta(seconds=0))
    if not p95:
        p95 = 0
    p99 = monitor_transactions_aggregates.get('p99', timedelta(seconds=0))
    if not p99:
        p99 = 0

    search_result_monitor_stats = MonitorStats(
        transaction_count=UInt64Value(value=total_count),
        finished_transaction_count=UInt64Value(value=monitor_transactions_finished.count()),
        transaction_avg_delay=DoubleValue(value=round(avg_delay, 3)),
        percentiles={'p95': round(p95, 3), 'p99': round(p99, 3)}
    )

    qs = qs.order_by('-created_at')

    qs = filter_page(qs, page)
    qs = qs.select_related('monitor')
    mt_protos = [mt.proto for mt in qs]

    return GetMonitorsTransactionsSearchQueryResponse(meta=get_meta(total_count=total_count, tr=dtr.to_tr(), page=page),
                                                      monitor_transactions=mt_protos,
                                                      search_result_monitor_stats=search_result_monitor_stats)


def get_monitor_transaction_status(status):
    if status == 2:
        return 'Finished'
    return 'Active'


@web_api(GetMonitorsTransactionsSearchQueryRequest)
@use_read_replica
def monitors_transactions_export(request_message: GetMonitorsTransactionsSearchQueryRequest) -> Union[
    GetMonitorsTransactionsSearchQueryResponse, HttpResponse]:
    # Search monitor transactions given a search request
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)

    qs = account.monitortransaction_set.all()
    qs = filter_dtr(qs, dtr, 'created_at')
    qs = monitor_transaction_search_engine.process_query(qs, request_message.query_request)
    qs = qs.annotate(transaction_time=(Cast(F('monitortransactionstats__stats__transaction_time'), FloatField())))

    qs = qs.select_related('monitor')
    mt_protos = [mt.proto_for_export for mt in qs]

    mt_ids = list(x.id for x in mt_protos)
    mt_events_mapping = MonitorTransactionEventMapping.objects.filter(account_id=account.id,
                                                                      monitor_transaction_id__in=mt_ids).values_list(
        'monitor_transaction_id', 'type', 'event_id')

    mt_events_map = {}
    for mapping in mt_events_mapping:
        if mapping[0] not in mt_events_map:
            mt_events_map[mapping[0]] = []
        mt_events_map[mapping[0]].append(mapping)

    events_map = {}
    events = Events.objects.filter(account_id=account.id, id__in=list(x[2] for x in mt_events_mapping)).values_list(
        'id', 'event_type_name', 'timestamp', 'ingested_event', 'processed_kvs')
    for event in events:
        events_map[event[0]] = event

    csv_data = []

    primary_event_keys_seq = []
    secondary_event_keys_seq = []

    finished_txn = qs.filter(type=MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED).first()
    if finished_txn:
        sample_mt_proto = finished_txn.proto_for_export
    else:
        sample_mt_proto = mt_protos[0]

    csv_data_row = ['Transaction Value', 'Monitor Name', 'Status', 'Has Alerts', 'Transaction Time']
    primary_event = list(filter(lambda x: x[1] == 1, mt_events_map[sample_mt_proto.id]))
    if primary_event:
        primary_event = primary_event[0]
        event_object = events_map[primary_event[2]]
        csv_data_row.append('primary_event_type')
        csv_data_row.append('primary_event_timestamp')
        for kv in json.loads(event_object[3])['kvs']:
            csv_data_row.append("primary_" + kv['key'])
            primary_event_keys_seq.append(kv['key'])

    secondary_event = list(filter(lambda x: x[1] == 2, mt_events_map[sample_mt_proto.id]))
    if secondary_event:
        secondary_event = secondary_event[0]
        event_object = events_map[secondary_event[2]]
        csv_data_row.append('secondary_event_type')
        csv_data_row.append('secondary_event_timestamp')
        for kv in json.loads(event_object[3])['kvs']:
            csv_data_row.append("secondary_" + kv['key'])
            secondary_event_keys_seq.append(kv['key'])

    csv_data.append(csv_data_row)

    for mt in mt_protos:
        csv_data_row = [mt.transaction, mt.monitor.name, get_monitor_transaction_status(mt.status), mt.has_alerts.value,
                        mt.transaction_time.value]
        primary_event = list(filter(lambda x: x[1] == 1, mt_events_map[mt.id]))
        if primary_event:
            primary_event = primary_event[0]
            event_object = events_map[primary_event[2]]
            csv_data_row.append(event_object[1])
            csv_data_row.append(event_object[2].strftime('%Y-%m-%d %H:%M:%S'))
            for k in primary_event_keys_seq:
                csv_data_row.append(event_object[4].get(k, None))

        secondary_event = list(filter(lambda x: x[1] == 2, mt_events_map[mt.id]))
        if secondary_event:
            secondary_event = secondary_event[0]
            event_object = events_map[secondary_event[2]]
            csv_data_row.append(event_object[1])
            csv_data_row.append(event_object[2].strftime('%Y-%m-%d %H:%M:%S'))
            for k in secondary_event_keys_seq:
                csv_data_row.append(event_object[4].get(k, None))

        csv_data.append(csv_data_row)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="file.csv"'
    writer = csv.writer(response)

    for row in csv_data:
        writer.writerow(row)
    return response


@web_api(GetMonitorsTransactionsExportQueryRequest)
@use_read_replica
def monitors_transactions_export_v2(request_message: GetMonitorsTransactionsExportQueryRequest) -> Union[
    GetMonitorsTransactionsExportQueryResponse, HttpResponse]:
    # Search monitor transactions given a search request
    account: Account = get_request_account()
    user: User = get_request_user()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    query_request = request_message.query_request

    export_id = uuid.uuid4().hex
    if GLOBAL_EXPORT_CONTEXT_CACHE.get(account.id, Context.MONITOR_TRANSACTION, user.email):
        export_id = GLOBAL_EXPORT_CONTEXT_CACHE.get(account.id, Context.EVENT, user.email)
    else:
        qs = account.monitortransaction_set.all()
        qs = filter_dtr(qs, dtr, 'created_at')
        qs = monitor_transaction_search_engine.process_query(qs, query_request)
        if qs.count() > 10000:
            return GetMonitorsTransactionsExportQueryResponse(meta=get_meta(), success=BoolValue(value=False),
                                                              message=Message(
                                                                  title="Monitor Transaction Export Failure",
                                                                  description="Export size too large"))
        else:
            GLOBAL_EXPORT_CONTEXT_CACHE.create_or_update(account.id, Context.MONITOR_TRANSACTION, user.email, export_id)
            export_task_request, message = export_task(account.id, Context.MONITOR_TRANSACTION, user.email,
                                                       proto_to_dict(request_message))

            if not export_task_request:
                return GetMonitorsTransactionsExportQueryResponse(meta=get_meta(), success=BoolValue(value=False),
                                                                  message=Message(
                                                                      title="Monitor Transaction Export Failure",
                                                                      description=message))

    return GetMonitorsTransactionsExportQueryResponse(meta=get_meta(), success=BoolValue(value=True),
                                                      export_context_id=export_id)


@web_api(SaveMonitorTransactionsSearchQueryRequest)
@use_read_replica
def save_monitor_transactions_search(request_message: SaveMonitorTransactionsSearchQueryRequest) -> Union[
    SaveMonitorTransactionsSearchQueryResponse, HttpResponse]:
    # Save events search context
    account: Account = get_request_account()

    generated_search_context_id = uuid.uuid4().hex
    query_request_dict = proto_to_dict(request_message.query_request)
    GLOBAL_MONITOR_TRANSACTION_QUERY_SEARCH_REQUEST_CACHE.create_or_update(account.id, generated_search_context_id,
                                                                           query_request_dict, None)

    return SaveMonitorTransactionsSearchQueryResponse(meta=get_meta(), query_context_id=generated_search_context_id)


@web_api(GetMonitorsTransactionsSearchV2QueryRequest)
@use_read_replica
def monitors_transactions_search_v2(request_message: GetMonitorsTransactionsSearchV2QueryRequest) -> Union[
    GetMonitorsTransactionsSearchV2QueryResponse, HttpResponse]:
    # V2 search monitor transactions given a search request
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    page = request_message.meta.page

    generated_search_context_id = None
    if request_message.save_query.value:
        generated_search_context_id = uuid.uuid4().hex
        query_request_dict = proto_to_dict(request_message.query_request)
        GLOBAL_MONITOR_TRANSACTION_QUERY_SEARCH_REQUEST_CACHE.create_or_update(account.id, generated_search_context_id,
                                                                               query_request_dict, None)

    qs = account.monitortransaction_set.all()
    qs = filter_dtr(qs, dtr, 'created_at')
    qs = monitor_transaction_search_engine.process_query(qs, request_message.query_request)
    total_count = qs.count()
    monitor_transactions_finished = qs.filter(type=MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED)

    monitor_transactions_aggregates = monitor_transactions_finished.annotate(
        transaction_time=(Cast(F('monitortransactionstats__stats__transaction_time'), FloatField()))
    ).aggregate(
        p95=Percentile('transaction_time', percentile=0.95),
        p99=Percentile('transaction_time', percentile=0.99),
        avg_delay=Avg(F('transaction_time'))
    )

    avg_delay = monitor_transactions_aggregates.get('avg_delay')
    if not avg_delay:
        avg_delay = 0

    p95 = monitor_transactions_aggregates.get('p95', timedelta(seconds=0))
    if not p95:
        p95 = 0
    p99 = monitor_transactions_aggregates.get('p99', timedelta(seconds=0))
    if not p99:
        p99 = 0

    search_result_monitor_stats = MonitorStats(
        transaction_count=UInt64Value(value=total_count),
        finished_transaction_count=UInt64Value(value=monitor_transactions_finished.count()),
        transaction_avg_delay=DoubleValue(value=round(avg_delay, 3)),
        percentiles={'p95': round(p95, 3), 'p99': round(p99, 3)}
    )

    qs = monitor_transaction_search_engine.process_ordering(qs, request_message.query_request)
    qs = qs.select_related('monitor')
    qs = qs.annotate(stats=Subquery(
        MonitorTransactionStats.objects.filter(monitor_transaction=OuterRef("pk")).values('stats').order_by(
            'created_at')[:1]
    ))

    qs = filter_page(qs, page)
    mt_details_proto = [mt.details_proto for mt in qs]

    return GetMonitorsTransactionsSearchV2QueryResponse(
        meta=get_meta(total_count=total_count, tr=dtr.to_tr(), page=page),
        monitor_transaction_details=mt_details_proto,
        search_result_monitor_stats=search_result_monitor_stats,
        query_context_id=generated_search_context_id
    )


@web_api(GetMetricExpressionOptionsRequest)
@use_read_replica
def metrics_options(request_message: GetMetricExpressionOptionsRequest) -> Union[
    GetMetricExpressionOptionsResponse, HttpResponse]:
    account: Account = get_request_account()

    metrics_options = get_metric_options(account, request_message.context, request_message.id_literal)
    metric_expression = get_default_metric_expression(account, request_message.context, request_message.id_literal)

    return GetMetricExpressionOptionsResponse(
        meta=get_meta(),
        metric_options=metrics_options,
        default_metric_expression=metric_expression
    )


@web_api(GetMetricRequest)
@use_read_replica
def metrics(request_message: GetMetricRequest) -> Union[GetMetricResponse, HttpResponse]:
    account: Account = get_request_account()
    meta: Meta = request_message.meta
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)

    metric_expressions = request_message.metric_expressions

    try:
        metric_data = process_metric_expressions(account, request_message.context, metric_expressions, dtr)
        return GetMetricResponse(success=BoolValue(value=True), metric_data=metric_data)
    except Exception as e:
        return GetMetricResponse(success=BoolValue(value=False), message=Message(
            description='The metric expression is invalid. Try changing the aggregation data or grouping keys'))


@web_api(GetPanelsV1Request)
def panels_v1_get(request_message: GetPanelsV1Request) -> Union[GetPanelsV1Response, HttpResponse]:
    account: Account = get_request_account()
    name: str = request_message.name
    panels = GLOBAL_PANEL_CACHE.get(account_id=account.id, name=name)

    if not panels:
        return GetPanelsV1Response(meta=get_meta(), panels=[])

    panel_protos: PanelV1 = [dict_to_proto(panel, PanelV1) for panel in panels]

    return GetPanelsV1Response(meta=get_meta(), panels=panel_protos)


@web_api(CreateOrUpdatePanelV1Request)
def panels_v1_create_or_update(request_message: CreateOrUpdatePanelV1Request) -> Union[
    CreateOrUpdatePanelV1Response, HttpResponse]:
    account: Account = get_request_account()

    panel: PanelV1 = request_message.panel

    if not panel or not panel.meta_info.name:
        return CreateOrUpdatePanelV1Response(success=BoolValue(value=False))

    GLOBAL_PANEL_CACHE.create_or_update(account_id=account.id, name=panel.meta_info.name, panel=proto_to_dict(panel))
    return CreateOrUpdatePanelV1Response(success=BoolValue(value=True))


@web_api(DeletePanelV1Request)
def panels_v1_delete(request_message: DeletePanelV1Request) -> Union[
    DeletePanelV1Response, HttpResponse]:
    account: Account = get_request_account()

    name: str = request_message.name

    if not name:
        return DeletePanelV1Response(success=BoolValue(value=False))

    dashboards = GLOBAL_DASHBOARD_CACHE.get(account_id=account.id)
    for dashboard in dashboards:
        panel_names = dashboard.get('panels', [])
        for d_p_name in panel_names:
            if d_p_name == name:
                panel_names.remove(name)
        GLOBAL_DASHBOARD_CACHE.create_or_update(account_id=account.id, name=dashboard.get('name'), dashboard=dashboard)

    GLOBAL_PANEL_CACHE.delete(account_id=account.id, name=name)
    return DeletePanelV1Response(success=BoolValue(value=True))


@web_api(GetDashboardsV1Request)
def dashboards_v1_get(request_message: GetDashboardsV1Request) -> Union[GetDashboardsV1Response, HttpResponse]:
    account: Account = get_request_account()
    name: str = request_message.name
    dashboards = GLOBAL_DASHBOARD_CACHE.get(account_id=account.id, name=name)

    if not dashboards:
        return GetDashboardsV1Response(meta=get_meta(), dashboards=[])

    for dashboard in dashboards:
        panels = []
        panel_names = dashboard.get('panels', [])
        for name in panel_names:
            panel = GLOBAL_PANEL_CACHE.get(account_id=account.id, name=name)
            panels.extend(panel)
        dashboard['panels'] = panels

    dashboard_protos: DashboardV1 = [dict_to_proto(dashboard, DashboardV1) for dashboard in dashboards]

    return GetDashboardsV1Response(meta=get_meta(), dashboards=dashboard_protos)


@web_api(CreateOrUpdateDashboardV1Request)
def dashboard_v1_create_or_update(request_message: CreateOrUpdateDashboardV1Request) -> Union[
    CreateOrUpdateDashboardV1Response, HttpResponse]:
    account: Account = get_request_account()

    dashboard: DashboardV1 = request_message.dashboard

    if not dashboard or not dashboard.name or not dashboard.panels:
        return CreateOrUpdateDashboardV1Response(success=BoolValue(value=False))

    panels = dashboard.panels
    panel_names = []
    for panel in panels:
        if not panel.meta_info or not panel.meta_info.name:
            return CreateOrUpdateDashboardV1Response(success=BoolValue(value=False))
        panel_names.append(panel.meta_info.name)
        if panel.data and panel.data.type == PanelData.PanelDataType.FUNNEL:
            try:
                entity_funnel, error = entity_funnels_create(account, panel)
                if error:
                    return CreateOrUpdateDashboardV1Response(success=BoolValue(value=False),
                                                             message=Message(title='Error creating entity funnel',
                                                                             description=error))
            except Exception as ex:
                logger.error('Error creating entity funnel', exc_info=True)
                return CreateOrUpdateDashboardV1Response(success=BoolValue(value=False),
                                                         message=Message(title='Error creating entity funnel',
                                                                         description=str(ex)))
        else:
            GLOBAL_PANEL_CACHE.create_or_update(account_id=account.id, name=panel.meta_info.name,
                                                panel=proto_to_dict(panel))

    dashboard_dict = proto_to_dict(dashboard)
    dashboard_dict['panels'] = panel_names
    GLOBAL_DASHBOARD_CACHE.create_or_update(account_id=account.id, name=dashboard.name, dashboard=dashboard_dict)

    return CreateOrUpdateDashboardV1Response(success=BoolValue(value=True))


@web_api(DeleteDashboardV1Request)
def dashboards_v1_delete(request_message: DeleteDashboardV1Request) -> Union[
    DeleteDashboardV1Response, HttpResponse]:
    account: Account = get_request_account()

    name: str = request_message.name

    if not name:
        return DeletePanelV1Response(success=BoolValue(value=False))

    if account.entity_set.filter(name=name, type=EntityProto.Type.FUNNEL).exists():
        try:
            entity_funnel = account.entity_set.get(name=name, type=EntityProto.Type.FUNNEL)
            entity_funnel_monitor_mapping_ids = list(
                account.entitymonitormapping_set.filter(entity=entity_funnel).filter(
                    is_active=True).values_list('id', flat=True))
            entity_funnel_update_ops: [UpdateEntityFunnelOp] = [
                UpdateEntityFunnelOp(op=UpdateEntityFunnelOp.Op.REMOVE_ENTITY_FUNNEL_MONITOR_MAPPINGS,
                                     remove_entity_funnel_monitor_mappings=UpdateEntityFunnelOp.RemoveEntityFunnelMonitorMappings(
                                         entity_funnel_monitor_mapping_ids=entity_funnel_monitor_mapping_ids)),
                UpdateEntityFunnelOp(op=UpdateEntityFunnelOp.Op.UPDATE_ENTITY_FUNNEL_STATUS,
                                     update_entity_funnel_status=UpdateEntityFunnelOp.UpdateEntityFunnelStatus(
                                         is_active=BoolValue(value=False)))
            ]
            entity_funnel_update_processor.update(entity_funnel, entity_funnel_update_ops)
        except Exception as ex:
            logger.error('Error deleting entity funnel', exc_info=True)
            return DeleteDashboardV1Response(success=BoolValue(value=False),
                                             message=Message(title='Error deleting entity funnel', description=str(ex)))

    GLOBAL_DASHBOARD_CACHE.delete(account_id=account.id, name=name)
    return DeleteDashboardV1Response(success=BoolValue(value=True))


@web_api(GetMonitorTriggerRequest)
def monitors_triggers_get(request_message: GetMonitorTriggerRequest) -> Union[GetMonitorTriggerResponse, HttpResponse]:
    account: Account = get_request_account()

    tr: TimeRange = request_message.meta.time_range
    page: Page = request_message.meta.page
    show_inactive = request_message.meta.show_inactive

    trigger_ids = request_message.trigger_ids
    monitor_id = request_message.monitor_id
    if monitor_id:
        event_triggers = account.trigger_set.filter(monitor_id=monitor_id)
        if not show_inactive or not show_inactive.value:
            event_triggers = event_triggers.filter(is_active=True)
    elif trigger_ids:
        event_triggers = account.trigger_set.filter(id__in=trigger_ids)
    else:
        return GetMonitorTriggerResponse(meta=get_meta())

    total_count = event_triggers.count()
    event_triggers = filter_page(event_triggers, page)
    trigger_protos = [t.proto for t in event_triggers]

    monitor_trigger_notifications: [MonitorTriggerNotificationDetail] = []
    for t in trigger_protos:
        notifications = account.notification_set.filter(trigger=t.id)
        notification_protos = [n.proto for n in notifications]
        monitor_trigger_notifications.append(
            MonitorTriggerNotificationDetail(trigger=t, notifications=notification_protos))

    return GetMonitorTriggerResponse(meta=get_meta(tr, page, total_count, show_inactive),
                                     monitor_trigger_notification_details=monitor_trigger_notifications)


@web_api(CreateMonitorTriggerRequest)
def monitors_triggers_create(request_message: CreateMonitorTriggerRequest) -> Union[
    CreateMonitorTriggerResponse, HttpResponse]:
    account: Account = get_request_account()

    triggers: [TriggerProto] = request_message.triggers
    notifications: [NotificationConfig] = request_message.notifications
    duplicate_triggers, err = create_monitor_triggers(account, triggers, notifications)
    if err:
        return CreateMonitorTriggerResponse(success=BoolValue(value=False), message=Message(description=err))
    elif duplicate_triggers:
        message = ''
        for dp_triggers in duplicate_triggers:
            message += dp_triggers.name
            message += ', '
        return CreateMonitorTriggerResponse(success=BoolValue(value=False),
                                            message=Message(title='Found duplicate trigger names', description=message))

    return CreateMonitorTriggerResponse(success=BoolValue(value=True))


@web_api(UpdateMonitorTriggerRequest)
def monitors_triggers_update(request_message: UpdateMonitorTriggerRequest) -> Union[
    UpdateMonitorTriggerResponse, HttpResponse]:
    account: Account = get_request_account()

    trigger_id = request_message.trigger_id.value
    if not trigger_id:
        return ProtoJsonResponse(
            UpdateMonitorTriggerResponse(
                success=BoolValue(value=False),
                message=Message(title='No trigger id defined in the request')
            ),
            status=400
        )

    qs: QuerySet = account.trigger_set.filter(id=trigger_id).select_related('monitor', 'monitor__primary_key',
                                                                            'monitor__secondary_key')
    if not qs.exists():
        return ProtoJsonResponse(
            UpdateMonitorTriggerResponse(
                success=BoolValue(value=False),
                message=Message(title=f'{trigger_id} defined in the request not found')
            ),
            status=400
        )

    trigger: Trigger = qs.first()
    try:
        monitor_trigger_update_processor.update(trigger, request_message.update_trigger_ops)
    except Exception as ex:
        return ProtoJsonResponse(
            UpdateMonitorTriggerResponse(
                success=BoolValue(value=False),
                message=Message(
                    title=f'Error updating entity {trigger.name}',
                    # description=f'{traceback.format_exception(type(ex), ex, ex.__traceback__)}'
                )
            ),
            status=400
        )
    return UpdateMonitorTriggerResponse(
        success=BoolValue(value=True),
        message=Message(title=f'Entity "{trigger.name}" updated successfully')
    )


@web_api(GetMonitorTriggerOptionsRequest)
def monitors_triggers_options(request_message: GetMonitorTriggerOptionsRequest) -> Union[
    GetMonitorTriggerOptionsResponse, HttpResponse]:
    user: User = get_request_user()
    account: Account = get_request_account()

    if not request_message.monitor_id:
        return GetMonitorTriggerOptionsResponse(meta=get_meta(), success=BoolValue(value=False),
                                                message=Message(description="Invalid request body",
                                                                title="Missing monitor id"))
    else:
        monitor = \
            account.monitor_set.filter(id=request_message.monitor_id).values('id', 'name', 'primary_key__event_type_id',
                                                                             'secondary_key__event_type_id')[0]

        event_keys = account.eventkey_set.filter(event_type_id__in=[monitor['primary_key__event_type_id'],
                                                                    monitor[
                                                                        'secondary_key__event_type_id']])
        event_key_options = [ek.proto for ek in event_keys if is_filterable_key_type(ek.type)]

    trigger_options: [TriggerOption] = get_default_trigger_options(scope=account)
    notification_options: [NotificationOption] = notification_client.get_notification_options(user, account)

    return GetMonitorTriggerOptionsResponse(meta=get_meta(), success=BoolValue(value=True),
                                            monitor=MonitorPartial(id=monitor['id'], name=monitor["name"]),
                                            primary_event_type=EventTypePartial(
                                                id=monitor['primary_key__event_type_id']),
                                            secondary_event_type=EventTypePartial(
                                                id=monitor['secondary_key__event_type_id']),
                                            monitor_trigger_options=MonitorTriggerOptions(
                                                default_trigger_options=trigger_options,
                                                notification_options=notification_options,
                                                event_key_filter_options=event_key_options))


@web_api(GetAlertsSummaryRequest)
def alerts_summary_get(request_message: GetAlertsSummaryRequest) -> Union[GetAlertsSummaryResponse, HttpResponse]:
    account: Account = get_request_account()

    tr: TimeRange = request_message.meta.time_range
    page: Page = request_message.meta.page

    if request_message.monitor_id:
        triggers = account.trigger_set.filter(monitor_id=request_message.monitor_id).values('id')
        trigger_ids = [trigger["id"] for trigger in triggers]
        event_alerts = account.alert_set.filter(trigger_id__in=trigger_ids)
    elif request_message.alert_ids:
        event_alerts = account.alert_set.filter(id__in=request_message.alert_ids)
    else:
        event_alerts = account.alert_set.all()

    qs = filter_time_range(event_alerts, tr, 'triggered_at')
    qs = qs.order_by('-triggered_at')
    qs = qs.select_related('trigger', 'trigger__monitor', 'trigger__monitor__primary_key',
                           'trigger__monitor__secondary_key', 'trigger__monitor__primary_key__event_type',
                           'trigger__monitor__secondary_key__event_type')
    total_count = qs.count()

    event_alerts = filter_page(qs, page)
    alert_summary_protos = [a.proto_summary for a in event_alerts]

    return GetAlertsSummaryResponse(meta=get_meta(tr=tr, page=page, total_count=total_count),
                                    alerts_summary=alert_summary_protos)


@web_api(GetAlertDetailsRequest)
def alerts_details_get(request_message: GetAlertDetailsRequest) -> Union[GetAlertDetailsResponse, HttpResponse]:
    account: Account = get_request_account()

    alert_id = request_message.alert_id

    if not alert_id:
        return GetAlertDetailsResponse(meta=get_meta(), alert_detail=AlertDetail())

    alert: Alert = account.alert_set.select_related('trigger', 'trigger__monitor', 'trigger__monitor__primary_key',
                                                    'trigger__monitor__secondary_key',
                                                    'trigger__monitor__primary_key__event_type',
                                                    'trigger__monitor__secondary_key__event_type').get(id=alert_id)

    if alert:
        return GetAlertDetailsResponse(meta=get_meta(), alert_detail=alert.proto_details)

    return GetAlertDetailsResponse(meta=get_meta(), alert_detail=AlertDetail())


@web_api(GetAlertMonitorTransactionsRequest)
def alerts_monitor_transactions_get(request_message: GetAlertMonitorTransactionsRequest) -> Union[
    GetAlertMonitorTransactionsResponse, HttpResponse]:
    account: Account = get_request_account()

    page: Page = request_message.meta.page
    alert_id = request_message.alert_id

    if not alert_id:
        return GetAlertMonitorTransactionsResponse(meta=get_meta(page=page))

    alert_mts = account.alertmonitortransactionmapping_set.filter(alert=alert_id).prefetch_related(
        'monitor_transaction').select_related('monitor_transaction__monitor')
    total_count = alert_mts.count()
    alert_mts = alert_mts.order_by('-created_at')
    alert_mts = filter_page(alert_mts, page)
    alert_mts_proto = [amt.proto for amt in alert_mts]
    return GetAlertMonitorTransactionsResponse(meta=get_meta(page=page, total_count=total_count),
                                               monitor_transactions=alert_mts_proto)


@web_api(GetNotificationConfigsRequest)
def notifications_get(request_message: GetNotificationConfigsRequest) -> Union[
    GetNotificationConfigsResponse, HttpResponse]:
    account: Account = get_request_account()

    if request_message.trigger_id:
        notifications = account.notification_set.filter(
            trigger=request_message.trigger_id)
    else:
        notifications = account.notification_set.all()

    notification_protos = [n.proto for n in notifications]

    return GetNotificationConfigsResponse(notification_configs=notification_protos)


@web_api(CreateNotificationConfigRequest)
def notifications_create(request_message: CreateNotificationConfigRequest) -> Union[
    CreateNotificationConfigResponse, HttpResponse]:
    account: Account = get_request_account()

    notification_config: NotificationConfig = request_message.notification_config

    channel_config = None
    which_one_of = notification_config.WhichOneof('config')
    if notification_config.channel == NotificationConfig.Channel.SLACK and which_one_of == 'slack_configuration':
        channel_config = proto_to_dict(notification_config.slack_configuration)

    if not notification_config.channel or not channel_config:
        return CreateNotificationConfigResponse(success=BoolValue(value=False),
                                                message=Message(title='Error creating notification',
                                                                description='Invalid payload'))

    Notification.objects.update_or_create(account=account,
                                          config=channel_config,
                                          defaults={
                                              'channel': notification_config.channel,
                                          })

    return CreateNotificationConfigResponse(success=BoolValue(value=True))


@web_api(GetGlobalSearchOptionsRequest)
def global_search_options_get(request_message: GetGlobalSearchOptionsRequest) -> Union[
    GetGlobalSearchOptionsResponse, HttpResponse]:
    return GetGlobalSearchOptionsResponse(meta=get_meta(),
                                          global_query_options=GlobalQueryOptions(op_descriptions=OP_DESCRIPTIONS,
                                                                                  op_mapping=OP_MAPPINGS,
                                                                                  literal_type_description=LITERAL_TYPE_DESCRIPTIONS))


@web_api(GetEventSearchOptionsRequest)
@use_read_replica
def event_search_options_get(request_message: GetEventSearchOptionsRequest) -> Union[
    GetEventSearchOptionsResponse, HttpResponse]:
    account: Account = get_request_account()

    default_query = None
    saved_query_request_context_id = request_message.saved_query_request_context_id.string.value
    if saved_query_request_context_id:
        saved_context = GLOBAL_EVENT_QUERY_SEARCH_REQUEST_CACHE.get(account.id, saved_query_request_context_id)
        if saved_context:
            default_query = dict_to_proto(saved_context, QueryRequest)

    obj = global_event_search_engine.get_obj(account, request_message.id_literal)
    if not default_query:
        default_query = global_event_search_engine.get_default_query(account, obj)

    options = global_event_search_engine.get_search_options(account, obj)
    return GetEventSearchOptionsResponse(meta=get_meta(),
                                         event_query_options=options,
                                         default_query_request=default_query)


@web_api(GetEntityOptionsRequest)
def entity_options_get(request_message: GetEntityOptionsRequest) -> Union[GetEntityOptionsResponse, HttpResponse]:
    account: Account = get_request_account()
    qs: QuerySet = account.eventkey_set.filter(type__in=TRANSACTIONAL_KEY_TYPES)
    qs = qs.prefetch_related('event_type')
    event_key_options = [ek.proto for ek in qs]
    return GetEntityOptionsResponse(entity_options=EntityOptions(event_key_options=event_key_options))


@web_api(CreateEntityRequest)
def entity_create(request_message: CreateEntityRequest) -> Union[CreateEntityResponse, HttpResponse]:
    account: Account = get_request_account()

    name = request_message.name.value
    if not name:
        return ProtoJsonResponse(
            CreateEntityResponse(
                success=BoolValue(value=False),
                message=Message(title='Entity creation failed', description='Missing name defined for the entity')
            ),
            status=400
        )
    event_key_ids = set(request_message.event_key_ids)
    if account.eventkey_set.filter(id__in=event_key_ids).count() != len(event_key_ids):
        return ProtoJsonResponse(
            CreateEntityResponse(
                success=BoolValue(value=False),
                message=Message(title='Entity creation failed', description='Invalid event keys selected')
            ),
            status=400
        )
    with dj_transaction.atomic():
        if account.entity_set.filter(name=name).exists():
            return CreateEntityResponse(
                success=BoolValue(value=False),
                message=Message(title='Entity creation failed', description=f'Entity with name {name} already exists')
            )
        e = Entity(
            account=account,
            name=name,
            is_active=request_message.is_active.value
        )
        e.save()

        eekms = [
            EntityEventKeyMapping(
                account=account, entity=e, event_key_id=event_key_id
            ) for event_key_id in request_message.event_key_ids
        ]

        if eekms:
            EntityEventKeyMapping.objects.bulk_create(
                eekms,
                ignore_conflicts=True,
                batch_size=25
            )

    return CreateEntityResponse(
        success=BoolValue(value=True),
        message=Message(
            title=f'Entity {name} created successfully'
        ),
        entity=e.proto_partial
    )


@web_api(UpdateEntityRequest)
def entity_update(request_message: UpdateEntityRequest) -> Union[UpdateEntityResponse, HttpResponse]:
    account: Account = get_request_account()

    entity_id = request_message.entity_id.value
    if not entity_id:
        return ProtoJsonResponse(
            UpdateEntityResponse(
                success=BoolValue(value=False),
                message=Message(title='No entity id defined in the request')
            ),
            status=400
        )

    qs: QuerySet = account.entity_set.filter(id=entity_id)
    if not qs.exists():
        return ProtoJsonResponse(
            UpdateEntityResponse(
                success=BoolValue(value=False),
                message=Message(title=f'{entity_id} defined in the request not found')
            ),
            status=400
        )

    entity: Entity = qs.first()
    entity_name = entity.name
    try:
        entity_update_processor.update(entity, request_message.update_entity_ops)
    except Exception as ex:
        return ProtoJsonResponse(
            UpdateEntityResponse(
                success=BoolValue(value=False),
                message=Message(
                    title=f'Error updating entity {entity_name}',
                    # description=f'{traceback.format_exception(type(ex), ex, ex.__traceback__)}'
                    description=f'{ex}'
                )
            ),
            status=400
        )
    return UpdateEntityResponse(
        success=BoolValue(value=True),
        message=Message(title=f'Entity "{entity.name}" updated successfully')
    )


@web_api(EntityTriggerOptionsRequest)
def entity_triggers_options(request_message: EntityTriggerOptionsRequest) -> Union[
    EntityTriggerOptionsResponse, HttpResponse]:
    account: Account = get_request_account()
    meta: Meta = request_message.meta
    dtr: DateTimeRange = to_dtr(meta.time_range)

    entity_id = request_message.entity_id
    qs: QuerySet = account.entity_set.filter(id=entity_id)
    entity = qs.first()

    event_type_ids = EntityEventKeyMapping.objects.prefetch_related('event_key__event_type').filter(
        entity=entity).values_list('event_key__event_type_id', flat=True)
    event_keys = account.eventkey_set.filter(event_type_id__in=event_type_ids)
    event_key_options = [ek.proto for ek in event_keys if is_filterable_key_type(ek.type)]

    return EntityTriggerOptionsResponse(meta=get_meta(tr=to_tr(dtr)), event_key_options=event_key_options,
                                        entity_name=entity.name)


@web_api(EntityTriggerCreateRequest)
def entity_triggers_create(request_message: EntityTriggerCreateRequest) -> Union[
    EntityTriggerCreateResponse, HttpResponse]:
    account: Account = get_request_account()
    trigger_name = request_message.trigger.name
    entity_id = request_message.trigger.entity_id
    notifications = request_message.notifications

    trigger_definition = request_message.trigger.definition
    trigger_filter = request_message.trigger.filter

    if not trigger_name:
        return EntityTriggerCreateResponse(
            message=Message(title='Trigger creation failed', description='Missing name defined for the trigger'))

    if not entity_id:
        return EntityTriggerCreateResponse(
            message=Message(title='Trigger creation failed', description='Missing entity id defined for the trigger'))

    entity = account.entity_set.filter(id=entity_id).first()
    db_trigger = EntityTrigger.objects.create(
        account=account, name=trigger_name, entity=entity, type=trigger_definition.type,
        rule_type=trigger_definition.rule_type,
        config=proto_to_dict(trigger_definition.trigger_rule_config), generated_config=proto_to_dict(trigger_filter)
    )

    if notifications:
        db_notifications = create_db_notifications(account, notifications)
        for db_n in db_notifications:
            EntityTriggerNotificationConfigMapping.objects.update_or_create(account=account, entity_trigger=db_trigger,
                                                                            notification=db_n)

    return EntityTriggerCreateResponse(message=Message(title='Trigger created'))


@web_api(EntityTriggerCreateRequest)
def entity_triggers_update(request_message: EntityTriggerCreateRequest) -> Union[
    EntityTriggerCreateResponse, HttpResponse]:
    account: Account = get_request_account()
    trigger_name = request_message.trigger.name
    trigger_id = request_message.trigger.id
    is_trigger_active = request_message.trigger.is_active.value
    notifications = request_message.notifications

    trigger_definition = request_message.trigger.definition
    trigger_filter = request_message.trigger.filter

    if not trigger_name:
        return EntityTriggerCreateResponse(
            message=Message(title='Trigger creation failed', description='Missing name defined for the trigger'))

    entity_trigger = EntityTrigger.objects.get(account=account, id=trigger_id)
    entity_trigger.name = trigger_name
    entity_trigger.type = trigger_definition.type
    entity_trigger.rule_type = trigger_definition.rule_type
    entity_trigger.config = proto_to_dict(trigger_definition.trigger_rule_config)
    entity_trigger.generated_config = proto_to_dict(trigger_filter)
    entity_trigger.is_active = is_trigger_active
    entity_trigger.save()

    # remove notification mappings
    EntityTriggerNotificationConfigMapping.objects.filter(account=account, entity_trigger=entity_trigger).delete()

    if notifications:
        db_notifications = create_db_notifications(account, notifications)
        for db_n in db_notifications:
            EntityTriggerNotificationConfigMapping.objects.update_or_create(account=account,
                                                                            entity_trigger=entity_trigger,
                                                                            notification=db_n)

    return EntityTriggerCreateResponse(message=Message(title='Trigger Updated'))


@web_api(EntityTriggerInactiveRequest)
def entity_triggers_inactivate(request_message: EntityTriggerInactiveRequest) -> Union[
    EntityTriggerInactiveResponse, HttpResponse]:
    account: Account = get_request_account()
    entity_trigger_id = request_message.entity_trigger_id

    if not entity_trigger_id:
        return EntityTriggerInactiveResponse(
            message=Message(title='Trigger inactivation failed', description='Missing entity trigger id'))

    EntityTrigger.objects.filter(
        account=account, id=entity_trigger_id
    ).update(is_active=False)

    return EntityTriggerInactiveResponse(message=Message(title='Trigger deactivated'))


@web_api(GetEntityTriggersRequest)
def entity_triggers_get(request_message: GetEntityTriggersRequest) -> Union[GetEntityTriggersResponse, HttpResponse]:
    account: Account = get_request_account()

    meta: Meta = request_message.meta
    dtr: DateTimeRange = to_dtr(meta.time_range)
    page = meta.page

    entity_id = request_message.entity_id
    entity_trigger_id = request_message.entity_trigger_id

    event_triggers = account.entitytrigger_set.filter(entity_id=entity_id, is_active=True)
    if entity_trigger_id:
        event_triggers = event_triggers.filter(id=entity_trigger_id)

    total_count = event_triggers.count()
    event_triggers = filter_page(event_triggers, page)
    trigger_protos = [t.proto for t in event_triggers]

    entity_trigger_notifications = []
    for t in trigger_protos:
        notifications = account.notification_set.filter(entity_trigger=t.id)
        notification_protos = [n.proto for n in notifications]
        entity_trigger_notifications.append(
            EntityTriggerNotificationDetail(trigger=t, notifications=notification_protos))

    return GetEntityTriggersResponse(meta=get_meta(tr=to_tr(dtr), page=page, total_count=total_count),
                                     entity_trigger_notification_details=entity_trigger_notifications)


@web_api(GetEntitySummaryRequest)
def entity_summary_get(request_message: GetEntitySummaryRequest) -> Union[GetEntitySummaryResponse, HttpResponse]:
    account: Account = get_request_account()

    meta: Meta = request_message.meta
    dtr: DateTimeRange = to_dtr(meta.time_range)
    page = meta.page
    show_inactive = meta.show_inactive

    qs: QuerySet = account.entity_set.filter(is_generated=False)
    if request_message.fuzzy_search_request.pattern:
        qs: QuerySet = entity_fuzzy_match_engine.match_pattern(account, request_message.fuzzy_search_request.pattern)

    if request_message.entity_ids:
        qs = qs.filter(id__in=request_message.entity_ids)

    if not show_inactive or not show_inactive.value:
        qs = qs.filter(is_active=True)

    total_count = qs.count()
    qs = filter_page(qs, page)

    entities = [entity.summary for entity in qs]
    return GetEntitySummaryResponse(
        meta=get_meta(tr=to_tr(dtr), page=page, total_count=total_count, show_inactive=show_inactive),
        entities=entities,
    )


@web_api(GetEntityDetailRequest)
def entity_detail_get(request_message: GetEntityDetailRequest) -> Union[GetEntityDetailResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)

    entity_id = request_message.entity_id.value
    if not entity_id:
        return JsonResponse({'message': 'No entity id defined in the request'}, status=400)

    qs: QuerySet = account.entity_set.filter(id=entity_id)
    if not qs.exists():
        return JsonResponse({'message': f'{entity_id} defined in the request not found'}, status=400)

    qs = qs.prefetch_related(
        'entityeventkeymapping_set',
        'entityeventkeymapping_set__event_key',
        'entityeventkeymapping_set__event_key__event_type'
    )
    entity: Entity = qs.first()

    return GetEntityDetailResponse(meta=get_meta(tr=to_tr(dtr)), entity=entity.detail_without_stats)


@web_api(GetEntityInstancesSummaryRequest)
def entity_instances_summary_get(request_message: GetEntityInstancesSummaryRequest) -> Union[
    GetEntityInstancesSummaryResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    page: Page = request_message.meta.page

    entity_id = request_message.entity_id.value
    if not entity_id:
        return JsonResponse({'message': 'No entity id defined in the request'}, status=400)
    if not account.entity_set.filter(id=entity_id).exists():
        return JsonResponse({'message': f'{entity_id} defined in the request not found'}, status=400)

    dtr_entity_instances = filter_dtr(
        account.entityinstanceeventmapping_set.filter(entity_id=entity_id),
        dtr,
        'created_at'
    )
    dtr_entity_instances = dtr_entity_instances.values('entity_instance_id').distinct().values_list(
        'entity_instance_id', flat=True
    )

    qs: QuerySet = account.entityinstance_set.filter(id__in=dtr_entity_instances)
    total_count = qs.count()
    qs = filter_page(qs.order_by('-created_at'), page)
    qs = annotate_entity_instance_stats(account, qs, dtr)

    entity_instances = [entity_instance.summary for entity_instance in qs]

    return GetEntityInstancesSummaryResponse(
        meta=get_meta(tr=to_tr(dtr), page=page, total_count=total_count),
        entity_instances=entity_instances
    )


@web_api(GetEntityInstancesDetailRequest)
def entity_instances_details_get(request_message: GetEntityInstancesDetailRequest) -> Union[
    GetEntityInstancesDetailResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    page: Page = request_message.meta.page

    entity_instance_id = request_message.entity_instance_id.value
    if not entity_instance_id:
        return JsonResponse({'message': 'No entity instance id defined in the request'}, status=400)
    qs: QuerySet = account.entityinstance_set.filter(id=entity_instance_id)

    if not qs.exists():
        return JsonResponse({'message': f'{entity_instance_id} defined in the request not found'}, status=400)

    qs = annotate_entity_instance_stats(account, qs, dtr)
    qs = qs.prefetch_related('entity')
    entity_instance = qs.first()

    return GetEntityInstancesDetailResponse(
        meta=get_meta(tr=to_tr(dtr), page=page),
        entity_instance=entity_instance.detail
    )


@web_api(GetEntityInstancesTimelineRequest)
@use_read_replica
def entity_instances_timeline_get(request_message: GetEntityInstancesTimelineRequest) -> Union[
    GetEntityInstancesTimelineResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    page: Page = request_message.meta.page

    entity_instance_id = request_message.entity_instance_id.value
    if not entity_instance_id:
        return JsonResponse({'message': 'No entity instance id defined in the request'}, status=400)
    qs: QuerySet = account.entityinstance_set.filter(id=entity_instance_id)

    if not qs.exists():
        return JsonResponse({'message': f'{entity_instance_id} defined in the request not found'}, status=400)

    entity_instance = qs.first()

    qs = account.entityinstanceeventmapping_set.filter(
        entity_instance=entity_instance
    ).order_by('-event_timestamp')

    total_count = qs.count()
    qs = annotate_entity_timeline(qs)

    event_id_record_dict = {}
    for rec in qs:
        event_id = rec['event_id']
        if event_id not in event_id_record_dict:
            event_id_record_dict[event_id] = EntityInstanceTimelineRecord(
                timestamp=int(rec['event_timestamp'].timestamp() * 1000),
                event=EventProto(
                    id=event_id,
                    event_type=EventTypePartial(
                        id=rec['event_type_id'],
                        name=rec['event_type_name']
                    ),
                    kvs=dict_to_proto(rec['event_event'], IngestionEvent).kvs
                ),
                transaction_event_type_mapping=[]
            )

        timeline_record: EntityInstanceTimelineRecord = event_id_record_dict[event_id]
        monitor = None
        transaction = None
        if 'monitor_id' in rec and rec['monitor_id']:
            monitor = MonitorPartial(
                id=rec['monitor_id'],
                name=rec['monitor_name']
            )
        if 'monitor_transaction_id' in rec and rec['monitor_transaction_id']:
            transaction = MonitorTransactionPartial(
                id=UInt64Value(value=rec['monitor_transaction_id']),
                transaction=StringValue(
                    value=rec['transaction']
                ),
                monitor=monitor
            )
            transaction_event_type = rec['transaction_event_type']

        qc: QuerySet = account.alertmonitortransactionmapping_set.all()
        qc = qc.prefetch_related('alert', 'alert__trigger')
        qc = qc.filter(monitor_transaction_id=rec['monitor_transaction_id'])

        for alert_monitor_transaction_mapping in qc:
            timeline_record.alerts.append(alert_monitor_transaction_mapping.miniproto)

        # if transaction:
        #     timeline_record.transaction_event_type_mapping.append(
        #         EntityInstanceTimelineRecord.MonitorTransactionEventTypeMapping(
        #             monitor_transaction=transaction,
        #             transaction_event_type=transaction_event_type,
        #             has_alerts=BoolValue(value=rec['monitor_transaction_has_alert'])
        #         )
        #     )

    sorted_events = sorted(event_id_record_dict.items(), key=lambda record: record[1].timestamp, reverse=True)
    recs = [rec for event_id, rec in sorted_events]

    return GetEntityInstancesTimelineResponse(
        meta=get_meta(tr=to_tr(dtr), page=page, total_count=total_count),
        entity_instance_timeline_records=recs,
    )


@web_api(GetEntityInstancesSearchOptionsRequest)
def entity_instance_search_options_get(request_message: GetEntityInstancesSearchOptionsRequest) -> Union[
    GetEntityInstancesSearchOptionsResponse, HttpResponse]:
    account: Account = get_request_account()

    obj = entity_instance_search_engine.get_obj(account, request_message.id_literal)
    options = entity_instance_search_engine.get_search_options(account, obj)
    default_query = entity_instance_search_engine.get_default_query(account, obj)

    return GetEntityInstancesSearchOptionsResponse(meta=get_meta(),
                                                   event_query_options=options,
                                                   default_query_request=default_query)


@web_api(GetEntityInstancesSearchOptionsV2Request)
def entity_instance_search_options_get_v2(request_message: GetEntityInstancesSearchOptionsV2Request) -> Union[
    GetEntityInstancesSearchOptionsV2Response, HttpResponse]:
    account: Account = get_request_account()

    obj = entity_instance_search_engine.get_obj(account, request_message.id_literal)
    options = entity_instance_search_engine.get_search_options_v2(account, obj)
    default_query = entity_instance_search_engine.get_default_query(account, obj)

    return GetEntityInstancesSearchOptionsV2Response(meta=get_meta(),
                                                     event_query_options=options,
                                                     default_query_request=default_query)


@web_api(GetEntityInstanceSearchQueryRequest)
@use_read_replica
def entity_instances_search(request_message: GetEntityInstanceSearchQueryRequest) -> Union[
    GetEntityInstanceSearchQueryResponse, HttpResponse]:
    # Search entity instances given a search request
    account: Account = get_request_account()
    page = request_message.meta.page
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)

    qs = account.entityinstance_set.all()
    qs = filter_dtr(qs, dtr, 'created_at')
    qs = entity_instance_search_engine.process_query(qs, request_message.query_request)

    total_count = qs.count()
    qs = qs.order_by('-created_at')
    qs = filter_page(qs, page)

    qs = annotate_entity_instance_stats(account, qs, dtr)
    qs = qs.prefetch_related('entity')

    entity_instances_protos = [ei.summary for ei in qs]

    return GetEntityInstanceSearchQueryResponse(meta=get_meta(total_count=total_count, tr=dtr.to_tr(), page=page),
                                                entity_instances=entity_instances_protos)


@web_api(GetEntityWorkflowSearchQueryRequest)
@use_read_replica
def entity_workflow_get(request_message: GetEntityWorkflowSearchQueryRequest) -> Union[
    GetEntityWorkflowSearchQueryResponse, HttpResponse]:
    # Search entity instances given a search request
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    entity_id = request_message.entity_id.value
    entity_instance_value = request_message.entity_instance_value

    is_single_key_name = False

    entity_event_key_type_metadata = account.entityeventkeymapping_set.filter(entity_id=entity_id).values(
        'event_key__name', 'event_key__event_type_id')
    event_type_ids = set([e['event_key__event_type_id'] for e in entity_event_key_type_metadata])
    event_type_key_name_mapping = {e['event_key__event_type_id']: e['event_key__name'] for e in
                                   entity_event_key_type_metadata}

    if len(set(event_type_key_name_mapping.values())) == 1:
        is_single_key_name = True

    if is_single_key_name:
        key_name = list(set(event_type_key_name_mapping.values()))[0]

        if entity_instance_value:
            events_group_query = "select groupArray(id) as id, groupArray(event_type_id) as event_type_id_group, groupArray(event_type_name) as event_type_name_group, groupArray(timestamp) as timestamp_group, e_id from (select id, event_type_id, event_type_name, timestamp, processed_kvs.{} as e_id from events where event_type_id in ({}) and account_id = {} and processed_kvs.{} = '{}' and timestamp between '{}' and '{}' order by timestamp) group by e_id;".format(
                key_name, ','.join([str(e) for e in event_type_ids]), account.id, key_name, entity_instance_value,
                dtr.to_tr_str()[0], dtr.to_tr_str()[1]
            )
        else:
            events_group_query = "select groupArray(id) as id, groupArray(event_type_id) as event_type_id_group, groupArray(event_type_name) as event_type_name_group, groupArray(timestamp) as timestamp_group, e_id from (select id, event_type_id, event_type_name, timestamp, processed_kvs.{} as e_id from events where event_type_id in ({}) and account_id = {} and timestamp between '{}' and '{}' order by timestamp) group by e_id;".format(
                key_name, ','.join([str(e) for e in event_type_ids]), account.id, dtr.to_tr_str()[0], dtr.to_tr_str()[1]
            )

        qs = Events.objects.raw(events_group_query)
        events_group_set = list(qs)

        g = NewGraph()

        for grouped_events in events_group_set:
            g.add_flow_grouped_events(grouped_events)

        wf_view = g.get_view()
    else:
        if entity_instance_value:
            entity_instance_value_query_string_arr = []
            for type_id in event_type_key_name_mapping:
                key_name = event_type_key_name_mapping[type_id]
                entity_instance_value_query_string_arr.append(
                    "(event_type_id = {} and processed_kvs.{} = '{}')".format(type_id, key_name, entity_instance_value))
            entity_instance_value_query_string = "( {} )".format(' OR '.join(entity_instance_value_query_string_arr))

            events_group_query = "SELECT id, account_id, created_at, timestamp, event_type_id, event_type_name, event_source, processed_kvs, ingested_event FROM events WHERE (account_id = {} AND {} AND timestamp >= '{}' AND timestamp < '{}');".format(
                account.id, entity_instance_value_query_string, dtr.to_tr_str()[0], dtr.to_tr_str()[1]
            )
        else:
            events_group_query = "SELECT id, account_id, created_at, timestamp, event_type_id, event_type_name, event_source, processed_kvs, ingested_event FROM events WHERE (account_id = {} AND event_type_id IN ({}) AND timestamp >= '{}' AND timestamp < '{}');".format(
                account.id, ','.join([str(e) for e in event_type_ids]), dtr.to_tr_str()[0], dtr.to_tr_str()[1]
            )

        qs = Events.objects.raw(events_group_query)
        events_set = list(qs)
        event_groups = defaultdict(list)

        g = Graph()

        for event in events_set:
            event_group_key_val = event.processed_kvs.get(event_type_key_name_mapping[event.event_type_id])
            event_groups[event_group_key_val].append(event)

        for grouped_events in event_groups.values():
            grouped_events.sort(key=lambda e: e.timestamp)
            g.add_flow_events(grouped_events)

        wf_view = g.get_view()

    return GetEntityWorkflowSearchQueryResponse(meta=get_meta(tr=dtr.to_tr()),
                                                workflow_view=wf_view)


@web_api(GetFunnelRequest)
@use_read_replica
def funnel_get_v2(request_message: GetFunnelRequest) -> Union[
    GetFunnelResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    funnel_event_type_ids = request_message.event_type_ids
    event_key_name = request_message.event_key_name
    filter_key_name = request_message.filter_key_name
    filter_value = request_message.filter_value

    ordered_funnel_data = entity_funnels_get_clickhouse_events(account, dtr, funnel_event_type_ids, event_key_name,
                                                               filter_key_name, filter_value)

    return GetFunnelResponse(meta=get_meta(tr=dtr.to_tr()), workflow_view=ordered_funnel_data)


@web_api(GetFunnelDropOffRequest)
@use_read_replica
def funnel_drop_off_distribution_get_v2(request_message: GetFunnelDropOffRequest) -> Union[
    GetFunnelDropOffDistributionResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)

    funnel_event_type_ids = request_message.funnel_event_type_ids
    funnel_key_name = request_message.funnel_key_name
    start_event_type_id = request_message.start_event_type_id
    end_event_type_id = request_message.end_event_type_id

    filter_key_name = request_message.filter_key_name
    filter_value = request_message.filter_value

    funnel_event_type_distribution, start_event_type_event_count = entity_funnels_get_clickhouse_drop_off_distribution(
        account, dtr, funnel_event_type_ids, funnel_key_name, start_event_type_id, end_event_type_id, filter_key_name,
        filter_value)
    if not funnel_event_type_distribution:
        return GetFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()))

    result_set = []
    for k, v in funnel_event_type_distribution.items():
        funnel_event_type_distribution_object = GetFunnelDropOffDistributionResponse.FunnelEventTypeDistribution(
            event_type_name=k, count=v)
        result_set.append(funnel_event_type_distribution_object)

    return GetFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()),
                                                funnel_event_type_distribution=result_set,
                                                previous_node_count=start_event_type_event_count)


@web_api(GetFunnelDropOffRequest)
@use_read_replica
def funnel_drop_off_get(request_message: GetFunnelDropOffRequest) -> Union[
    GetFunnelDropOffResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)

    funnel_event_type_ids = request_message.funnel_event_type_ids
    funnel_key_name = request_message.funnel_key_name
    start_event_type_id = request_message.start_event_type_id
    end_event_type_id = request_message.end_event_type_id

    filter_key_name = request_message.filter_key_name
    filter_value = request_message.filter_value

    csv_data = entity_funnels_get_clickhouse_drop_off_distribution_download(account, dtr, funnel_event_type_ids,
                                                                            funnel_key_name,
                                                                            start_event_type_id, end_event_type_id,
                                                                            filter_key_name, filter_value)

    if not csv_data:
        return GetFunnelDropOffResponse(meta=get_meta(tr=dtr.to_tr()))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="file.csv"'
    writer = csv.writer(response)

    for row in csv_data:
        writer.writerow(row)

    return response


@web_api(WorkflowBuilderRequest)
@use_read_replica
def workflow_builder(request_message: WorkflowBuilderRequest) -> Union[
    GetFunnelResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    workflow_config = json.loads(request_message.workflow_config)

    try:
        wb = WorkflowBuilder(dtr, account)
        wb.process_workflow_config(workflow_config)
        w_view = wb.get_workflow_view()

        return GetFunnelResponse(meta=get_meta(tr=dtr.to_tr()), workflow_view=w_view)
    except Exception as e:
        print(str(e))
        return GetFunnelResponse(
            message=str("Something went wrong. Please check your config. If you think it is correct, report it."))


@web_api(WorkflowBuilderRequest)
@use_read_replica
def workflow_node_metrics_timeseries(request_message: WorkflowBuilderRequest) -> Union[
    WorkflowTimeSeriesResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    workflow_config = json.loads(request_message.workflow_config)

    parsed_workflow_config = workflow_config
    config = parsed_workflow_config['config']
    compare_to = parsed_workflow_config['compare_to']

    name = config.get('name')
    metrics = config.get('metrics')

    metric_series_responses = []

    for metric in metrics:
        metric_name = metric.get('name')
        metric_source = metric.get('source')
        metric_expr = metric.get('expr')

        if metric_source == 'Datadog':
            dd_connector = DatadogConnector(dtr.to_tr(), account.id)
            metric_series = dd_connector.fetch_metric_timeseries(metric_expr)
            output_metric_series = [
                WorkflowTimeSeriesResponse.MetricValue(timestamp=int(item['timestamp']),
                                                       value=item['value'])
                for item in metric_series['series']
            ]

            if compare_to:
                prev_dtr = dtr.get_prev_dtr(compare_to)
                past_metric_series = dd_connector.fetch_metric_timeseries(metric_expr, prev_dtr.to_tr())
                past_output_metric_series = [
                    WorkflowTimeSeriesResponse.MetricValue(timestamp=int(item['timestamp']),
                                                           value=item['value'])
                    for item in past_metric_series['series']
                ]
                metric_series_responses.append(
                    WorkflowTimeSeriesResponse.MetricTimeSeries(metric_name=metric_name, metric_source=metric_source,
                                                                current_series=output_metric_series,
                                                                past_series=past_output_metric_series))
            else:
                metric_series_responses.append(
                    WorkflowTimeSeriesResponse.MetricTimeSeries(metric_name=metric_name, metric_source=metric_source,
                                                                current_series=output_metric_series))

        if metric_source == 'Newrelic':
            nr_connector = NewRelicConnector(dtr.to_tr(), account.id)
            metric_series = nr_connector.fetch_metric_timeseries(metric_expr)
            output_metric_series = [
                WorkflowTimeSeriesResponse.MetricValue(
                    timestamp=int(datetime.fromisoformat(item['from']).timestamp() * 1000),
                    value=item['values'][metric_series["metric_type"]])
                for item in metric_series['series']
            ]

            if compare_to:
                prev_dtr = dtr.get_prev_dtr(compare_to)
                past_metric_series = nr_connector.fetch_metric_timeseries(metric_expr, prev_dtr.to_tr())
                past_output_metric_series = [
                    WorkflowTimeSeriesResponse.MetricValue(
                        timestamp=int(datetime.fromisoformat(item['from']).timestamp() * 1000),
                        value=item['values'][past_metric_series["metric_type"]])
                    for item in past_metric_series['series']
                ]
                metric_series_responses.append(
                    WorkflowTimeSeriesResponse.MetricTimeSeries(metric_name=metric_name, metric_source=metric_source,
                                                                current_series=output_metric_series,
                                                                past_series=past_output_metric_series))
            else:
                metric_series_responses.append(
                    WorkflowTimeSeriesResponse.MetricTimeSeries(metric_name=metric_name, metric_source=metric_source,
                                                                current_series=output_metric_series))

        if metric_source == 'DrDroid':
            metric_series = process_workflow_metric_expression(account, metric_expr, dtr)
            output_metric_series = [
                WorkflowTimeSeriesResponse.MetricValue(
                    timestamp=item['timestamp'],
                    value=item['value'])
                for item in metric_series
            ]

            if compare_to:
                prev_dtr = dtr.get_prev_dtr(compare_to)
                past_metric_series = process_workflow_metric_expression(account, metric_expr, prev_dtr)
                past_output_metric_series = [
                    WorkflowTimeSeriesResponse.MetricValue(
                        timestamp=item['timestamp'],
                        value=item['value'])
                    for item in past_metric_series
                ]
                metric_series_responses.append(
                    WorkflowTimeSeriesResponse.MetricTimeSeries(metric_name=metric_name, metric_source=metric_source,
                                                                current_series=output_metric_series,
                                                                past_series=past_output_metric_series))
            else:
                metric_series_responses.append(
                    WorkflowTimeSeriesResponse.MetricTimeSeries(metric_name=metric_name, metric_source=metric_source,
                                                                current_series=output_metric_series))

    return WorkflowTimeSeriesResponse(meta=get_meta(tr=dtr.to_tr()), compare_to=compare_to, node_name=name,
                                      metric_time_series=metric_series_responses)


def get_index_in_array(arr, elem):
    if elem in arr:
        return arr.index(elem)
    return 100


@web_api(GetFunnelRequestV3)
@use_read_replica
def funnel_get_v3(request_message: GetFunnelRequestV3) -> Union[
    GetFunnelResponseV3, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    event_key_name = 'recordId'
    global_key_name = 'connectorId'
    filter_value = request_message.filter_value

    EVENTS_ORDER = {
        'Ingestion': ['p1-startIngestion', 'p1-unarchiveFile', 'p1-unarchive', ['p1-metadataRead', 'p2-audioReceived'],
                      'p1-transform', 'p1-normalize'],
        'p1': ['p1-startEvent', ['p1-success', 'p1-failed', 'p1-error'], 'p1-endEvent'],
        'p2': ['p2-startEvent', ['p2-success', 'p2-failed', 'p2-error'], 'p2-endEvent'],
        'p3': ['p3-startEvent', 'p3-filteredRecord', 'p3-success', 'p3-endEvent'],
        'p4': ['p4-startEvent', 'p4-asrInit', 'p4-success', 'p4-endEvent'],
        'ad': ['ad-startEvent', 'ad-dgInit', 'ad-dgCallbackStart', ['ad-dgCallbackSuccess', 'ad-dgCallbackError'],
               'ad-dgCallbackEnd', 'ad-success', 'ad-endEvent', ],
        'p5': ['p5-startEvent', 'p5-success', 'p5-endEvent'],
        'p5_1': ['p5_1-startEvent', ['p5_1-success', 'p5_1-failed'], 'p5_1-endEvent'],
        'p6': ['p6-startEvent', ['p6-success', 'p6-failed'], 'p6-endEvent'],
        'INGESTION_COMPLETE': ['INGESTION_COMPLETE']
    }

    events_group_query = "select count(distinct id) as id, count(distinct processed_kvs.{}) as unique_records, event_type_id, event_type_name from events where account_id = {} and timestamp between '{}' and '{}' group by event_type_id, event_type_name;".format(
        event_key_name, account.id, dtr.to_tr_str()[0],
        dtr.to_tr_str()[1]
    )

    if filter_value:
        events_group_query = "select count(distinct id) as id, count(distinct processed_kvs.{}) as unique_records, event_type_id, event_type_name from events where account_id = {} and timestamp between '{}' and '{}' and processed_kvs.{} = '{}' group by event_type_id, event_type_name;".format(
            event_key_name, account.id, dtr.to_tr_str()[0],
            dtr.to_tr_str()[1],
            global_key_name,
            filter_value
        )

    print(events_group_query)
    qs = Events.objects.raw(events_group_query)
    events_group_set = list(qs)

    events_group_dict = {}
    for node in events_group_set:
        events_group_dict[node.event_type_name] = node

    groups_dict = {}
    for stage in EVENTS_ORDER.keys():
        groups_dict[stage] = []
        for event in EVENTS_ORDER[stage]:
            if isinstance(event, list):
                temp_e = []
                for e in event:
                    if e in events_group_dict.keys():
                        temp_e.append(events_group_dict[e])
                groups_dict[stage].append(temp_e)
            else:
                if event in events_group_dict.keys():
                    groups_dict[stage].append(events_group_dict[event])

    stages = []
    for prefix, nodes in groups_dict.items():
        events = []
        for node in nodes:
            if isinstance(node, list):
                child_nodes = []
                for n in node:
                    child_nodes.append(GetFunnelResponseV3.stage_data.event_data(event_name=n.event_type_name,
                                                                                 event_id=n.event_type_id,
                                                                                 unique_records_count=n.unique_records,
                                                                                 count=n.id))
                events.append(GetFunnelResponseV3.stage_data.event_data(child_events=child_nodes))
            else:
                events.append(GetFunnelResponseV3.stage_data.event_data(event_name=node.event_type_name,
                                                                        event_id=node.event_type_id,
                                                                        unique_records_count=node.id, count=node.id))
        stages.append(GetFunnelResponseV3.stage_data(stage=prefix, events=events))

    return GetFunnelResponseV3(meta=get_meta(tr=dtr.to_tr()), stages=stages)


@web_api(CreateEntityFunnelRequest)
@use_read_replica
def entity_funnel_create(request_message: CreateEntityFunnelRequest) -> Union[CreateEntityFunnelResponse, HttpResponse]:
    account: Account = get_request_account()
    try:
        entity_funnel, error = entity_funnels_create(account, request_message.entity_funnel_panel)
        if entity_funnel:
            return CreateEntityFunnelResponse(success=BoolValue(value=True), funnel_entity=entity_funnel.proto_partial)
        if error:
            return CreateEntityFunnelResponse(success=BoolValue(value=False),
                                              message=Message(title="Entity Funnel Panel Creation Failure",
                                                              description=error))
    except Exception as e:
        logger.error(str(e))
        return CreateEntityFunnelResponse(success=BoolValue(value=False),
                                          message=Message(title="Entity Funnel Panel Creation Failure",
                                                          description=str(e)))


@web_api(GetEntityFunnelRequest)
@use_read_replica
def entity_funnel_get(request_message: GetEntityFunnelRequest) -> Union[GetEntityFunnelResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    entity_funnel_name = request_message.entity_funnel_name
    filter_key_name = request_message.filter_key_name
    filter_value = request_message.filter_value
    try:
        workflow_view = entity_funnels_get(account, dtr, entity_funnel_name, filter_key_name, filter_value)
        if workflow_view:
            return GetEntityFunnelResponse(meta=get_meta(tr=dtr.to_tr()), success=BoolValue(value=True),
                                           workflow_view=workflow_view)
        else:
            return GetEntityFunnelResponse(meta=get_meta(tr=dtr.to_tr()), success=BoolValue(value=True),
                                           message=Message(title="No Funnel Data Found"))
    except EntityFunnelCrudNotFoundException:
        try:
            funnel_event_type_ids, event_key_name, filter_key_name, filter_value = get_funnel_panel_data(account,
                                                                                                         entity_funnel_name,
                                                                                                         filter_key_name,
                                                                                                         filter_value)
            workflow_view = entity_funnels_get_clickhouse_events(account, dtr, funnel_event_type_ids, event_key_name,
                                                                 filter_key_name, filter_value)
            if workflow_view:
                return GetEntityFunnelResponse(meta=get_meta(tr=dtr.to_tr()), success=BoolValue(value=True),
                                               workflow_view=workflow_view)
            else:
                return GetEntityFunnelResponse(meta=get_meta(tr=dtr.to_tr()), success=BoolValue(value=False),
                                               message=Message(title="No Funnel Data Found"))
        except Exception as e:
            logger.error(str(e))
            return GetEntityFunnelResponse(meta=get_meta(tr=dtr.to_tr()), success=BoolValue(value=False),
                                           message=Message(title="Entity Funnel Panel Not Found",
                                                           traceback=str(e)))
    except Exception as e:
        logger.error(str(e))
        return GetEntityFunnelResponse(meta=get_meta(tr=dtr.to_tr()), success=BoolValue(value=False),
                                       message=Message(title="Failed to load Entity Funnel Panel", traceback=str(e)))


@web_api(UpdateEntityFunnelRequest)
@use_read_replica
def entity_funnel_update(request_message: UpdateEntityFunnelRequest) -> Union[UpdateEntityFunnelResponse, HttpResponse]:
    account: Account = get_request_account()

    entity_funnel_id = request_message.entity_funnel_id.value
    if not entity_funnel_id:
        return ProtoJsonResponse(
            UpdateEntityFunnelResponse(
                success=BoolValue(value=False),
                message=Message(title='No entity funnel id defined in the request')
            ),
            status=400
        )

    qs: QuerySet = account.entity_set.filter(id=entity_funnel_id)
    if not qs.exists():
        return ProtoJsonResponse(
            UpdateEntityFunnelResponse(
                success=BoolValue(value=False),
                message=Message(title=f'{entity_funnel_id} defined in the request not found')
            ),
            status=400
        )

    entity_funnel: Entity = qs.first()
    try:
        entity_funnel_update_processor.update(entity_funnel, request_message.update_entity_funnel_ops)
    except Exception as ex:
        logger.error(str(ex))
        return ProtoJsonResponse(
            UpdateEntityFunnelResponse(
                success=BoolValue(value=False),
                message=Message(
                    title=f'Error updating entity {entity_funnel.name}',
                )
            ),
            status=400
        )
    return UpdateEntityFunnelResponse(
        success=BoolValue(value=True),
        message=Message(title=f'Entity "{entity_funnel.name}" updated successfully')
    )


@web_api(GetEntityFunnelDropOffRequest)
@use_read_replica
def entity_funnel_drop_off_distribution_get(request_message: GetEntityFunnelDropOffRequest) -> Union[
    GetEntityFunnelDropOffDistributionResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)

    entity_funnel_name = request_message.entity_funnel_name
    funnel_key_name = request_message.funnel_key_name
    start_event_type_id = request_message.start_event_type_id
    end_event_type_id = request_message.end_event_type_id

    filter_key_name = request_message.filter_key_name
    filter_value = request_message.filter_value
    try:
        funnel_event_type_distribution, start_event_type_event_count = entity_funnels_drop_off_get(account, dtr,
                                                                                                   entity_funnel_name,
                                                                                                   funnel_key_name,
                                                                                                   start_event_type_id,
                                                                                                   end_event_type_id,
                                                                                                   filter_key_name,
                                                                                                   filter_value)
        if not funnel_event_type_distribution:
            return GetEntityFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()),
                                                              success=BoolValue(value=True), message=Message(
                    title="No Entity Funnel Drop off data found"))
    except EntityFunnelCrudNotFoundException:
        try:
            funnel_event_type_ids, event_key_name, filter_key_name, filter_value = get_funnel_panel_data(account,
                                                                                                         entity_funnel_name,
                                                                                                         filter_key_name,
                                                                                                         filter_value)
            funnel_event_type_distribution, start_event_type_event_count = entity_funnels_get_clickhouse_drop_off_distribution(
                account, dtr,
                funnel_event_type_ids,
                event_key_name,
                start_event_type_id,
                end_event_type_id,
                filter_key_name,
                filter_value)

            if not funnel_event_type_distribution:
                return GetEntityFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()),
                                                                  success=BoolValue(value=True), message=Message(
                        title="No Entity Funnel Drop off data found"))
        except Exception as e:
            logger.error(str(e))
            return GetEntityFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()),
                                                              success=BoolValue(value=True),
                                                              message=Message(
                                                                  title="Entity Funnel Panel Not Found",
                                                                  traceback=str(e)))
    except Exception as e:
        logger.error(str(e))
        return GetEntityFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()), success=BoolValue(value=True),
                                                          message=Message(
                                                              title="Failed to load Entity Funnel Drop off data",
                                                              traceback=str(e)))

    result_set = []
    for k, v in funnel_event_type_distribution.items():
        funnel_event_type_distribution_object = GetFunnelDropOffDistributionResponse.FunnelEventTypeDistribution(
            event_type_name=k, count=v)
        result_set.append(funnel_event_type_distribution_object)

    return GetFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()),
                                                funnel_event_type_distribution=result_set,
                                                previous_node_count=start_event_type_event_count)


@web_api(GetEntityFunnelDropOffRequest)
@use_read_replica
def entity_funnel_drop_off_distribution_download(request_message: GetEntityFunnelDropOffRequest) -> Union[
    GetEntityFunnelDropOffDistributionResponse, HttpResponse]:
    account: Account = get_request_account()
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)

    entity_funnel_name = request_message.entity_funnel_name
    funnel_key_name = request_message.funnel_key_name
    start_event_type_id = request_message.start_event_type_id
    end_event_type_id = request_message.end_event_type_id

    filter_key_name = request_message.filter_key_name
    filter_value = request_message.filter_value
    try:
        csv_data = entity_funnels_drop_off_download(account, dtr,
                                                    entity_funnel_name,
                                                    funnel_key_name,
                                                    start_event_type_id,
                                                    end_event_type_id,
                                                    filter_key_name,
                                                    filter_value)
        if not csv_data:
            return GetEntityFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()),
                                                              success=BoolValue(value=True), message=Message(
                    title="No Entity Funnel Drop off data found"))
    except EntityFunnelCrudNotFoundException:
        try:
            funnel_event_type_ids, event_key_name, filter_key_name, filter_value = get_funnel_panel_data(account,
                                                                                                         entity_funnel_name,
                                                                                                         filter_key_name,
                                                                                                         filter_value)
            csv_data = entity_funnels_get_clickhouse_drop_off_distribution_download(account, dtr,
                                                                                    funnel_event_type_ids,
                                                                                    event_key_name,
                                                                                    start_event_type_id,
                                                                                    end_event_type_id,
                                                                                    filter_key_name,
                                                                                    filter_value)
            if not csv_data:
                return GetEntityFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()),
                                                                  success=BoolValue(value=True), message=Message(
                        title="No Entity Funnel Drop off data found"))
        except Exception as e:
            logger.error(str(e))
            return GetEntityFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()),
                                                              success=BoolValue(value=True),
                                                              message=Message(
                                                                  title="Entity Funnel Panel Not Found",
                                                                  traceback=str(e)))
    except Exception as e:
        logger.error(str(e))
        return GetEntityFunnelDropOffDistributionResponse(meta=get_meta(tr=dtr.to_tr()), success=BoolValue(value=True),
                                                          message=Message(
                                                              title="Failed to load Entity Funnel Drop off data",
                                                              traceback=str(e)))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="file.csv"'
    writer = csv.writer(response)

    for row in csv_data:
        writer.writerow(row)

    return response
