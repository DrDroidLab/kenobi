import logging
from datetime import datetime
from typing import Union

import pytz
from django.core.mail import send_mail

from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string

from django.db.utils import IntegrityError

from google.protobuf.struct_pb2 import Struct
from google.protobuf.wrappers_pb2 import BoolValue, UInt64Value, StringValue

from accounts.models import Account, get_request_account, get_request_user, User
from connectors.crud.event_stream_processing_crud import get_or_create_event_processing_filter, \
    update_or_create_event_processing_filter, get_or_create_event_processing_parser, \
    update_or_create_event_processing_parser, get_or_create_event_processing_filter_parsers
from connectors.engine.event_stream_processing_filter_engine import filter_events
from connectors.engine.event_stream_processing_parser_engine import parse_events, \
    generated_drd_events_from_parsed_event_string
from connectors.utils import find_datetime_format_and_convert
from event.clickhouse.models import RawEventStreamData, FilterParsedEventData
from protos.event.api_pb2 import CreateConnectorRequest, CreateConnectorResponse, Message, RequestConnectorAPIRequest, \
    RequestConnectorAPIResponse, CreateTransformerMappingRequest, CreateTransformerMappingResponse, \
    GetConnectorKeysRequest, GetConnectorKeysResponse, SaveConnectorKeysResponse, SaveConnectorKeysRequest, \
    EventProcessingFiltersGetRequest, EventProcessingFiltersGetResponse, EventProcessingFiltersCreateRequest, \
    EventProcessingFiltersCreateResponse, EventProcessingFiltersUpdateRequest, EventProcessingFiltersUpdateResponse, \
    FilterEventsGetRequest, FilterEventsGetResponse, EventProcessingParsersGetRequest, \
    EventProcessingParsersGetResponse, EventProcessingParsersCreateRequest, EventProcessingParsersCreateResponse, \
    EventProcessingParsersUpdateRequest, EventProcessingParsersUpdateResponse, ParseFilteredEventsGetRequest, \
    ParseFilteredEventsGetResponse, GenerateDRDParsedEventsGetRequest, GenerateDRDParsedEventsGetResponse, \
    EventProcessingFiltersParsersCreateRequest, EventProcessingFiltersParsersCreateResponse
from connectors.models import Connector, ConnectorKey, ConnectorRequest, TransformerMapping
from protos.event.base_pb2 import TimeRange

from protos.event.connectors_pb2 import Connector as ConnectorProto, ConnectorKey as ConnectorKeyProto, ConnectorType, \
    DecoderType, TransformerType
from protos.event.schema_pb2 import IngestionEvent
from protos.event.stream_processing_pb2 import EventProcessingFilter as EventProcessingFilterProto, \
    EventProcessingParser as EventProcessingParserProto
from protos.kafka.event_stream_pb2 import StreamEvent
from prototype.db.decorator import use_read_replica
from prototype.utils.decorators import web_api
from prototype.utils.meta import get_meta
from prototype.utils.queryset import filter_page, filter_time_range

from utils.proto_utils import proto_to_dict

logger = logging.getLogger(__name__)


@web_api(RequestConnectorAPIRequest)
def connectors_request(request_message: RequestConnectorAPIRequest) -> Union[
    RequestConnectorAPIResponse, HttpResponse]:
    account: Account = get_request_account()
    user: User = get_request_user()

    connector_type: ConnectorType = request_message.connector_type

    if not connector_type or connector_type == ConnectorType.UNKNOWN:
        return RequestConnectorAPIResponse(success=BoolValue(value=False),
                                           message=Message(title="Invalid Connector Request",
                                                           description="Input Connector not supported yet"))

    connectors_request, created = ConnectorRequest.objects.get_or_create(account=account,
                                                                         connector_type=connector_type,
                                                                         defaults={
                                                                             'account': account,
                                                                             'connector_type': connector_type,
                                                                         })

    if not created:
        return RequestConnectorAPIResponse(success=BoolValue(value=False), message=Message(title="Duplicate Request",
                                                                                           description="Connector already requested"))

    connector_name = ''
    for k, v in ConnectorType.items():
        if connector_type == v:
            connector_name = k
            break

    recipient_email_id = user.email
    timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S %d-%m-%Y")
    msg_html = render_to_string('connector_reqeust_email_template.html',
                                {'connector_type': connector_name.capitalize(),
                                 'user_name': recipient_email_id,
                                 'timestamp': timestamp})
    send_mail(
        subject="Connector Request",
        message="test",
        from_email=None,
        recipient_list=[recipient_email_id, "dipesh@drdroid.io", "siddarth@drdroid.io"],
        html_message=msg_html
    )

    return RequestConnectorAPIResponse(success=BoolValue(value=True))


@web_api(CreateConnectorRequest)
def connectors_create(request_message: CreateConnectorRequest) -> Union[
    CreateConnectorResponse, HttpResponse]:
    account: Account = get_request_account()

    connector: ConnectorProto = request_message.connector
    connector_type = connector.type
    connector_keys = request_message.connector_keys

    if connector_type == ConnectorType.SENTRY:
        config = proto_to_dict(connector.sentry_config)

    try:
        with transaction.atomic():
            db_connector = Connector(account=account,
                                     name=connector.name.value,
                                     connector_type=connector_type,
                                     is_active=connector.is_active.value,
                                     metadata=config)
            db_connector.save()

            for c_key in connector_keys:
                connector_key: ConnectorKeyProto = c_key
                db_connector_key = ConnectorKey(account=account,
                                                connector=db_connector,
                                                key_type=connector_key.key_type,
                                                key=connector_key.key.value,
                                                is_active=connector_key.is_active.value)
                db_connector_key.save()
    except IntegrityError:
        return CreateConnectorResponse(success=BoolValue(value=False),
                                       message=Message(title='Failed to create connector'))

    return CreateConnectorResponse(success=BoolValue(value=True))


@web_api(CreateTransformerMappingRequest)
def transformer_mapping_create(request_message: CreateTransformerMappingRequest) -> Union[
    CreateTransformerMappingResponse, HttpResponse]:
    account: Account = get_request_account()

    if request_message.account_id.value:
        account = Account.objects.get(id=request_message.account_id.value)
    decoder_type: DecoderType = request_message.decoder_type
    transformer_type: TransformerType = request_message.transformer_type

    try:
        with transaction.atomic():
            db_transformer_mapping = TransformerMapping(account=account,
                                                        decoder_type=decoder_type,
                                                        transformer_type=transformer_type,
                                                        is_active=True)
            db_transformer_mapping.save()
    except IntegrityError:
        return CreateConnectorResponse(success=BoolValue(value=False),
                                       message=Message(title='Failed to create transformer mapping'))

    return CreateTransformerMappingResponse(success=BoolValue(value=True))


@web_api(GetConnectorKeysRequest)
def get_keys(request_message: GetConnectorKeysRequest) -> Union[
    GetConnectorKeysResponse, HttpResponse]:
    account: Account = get_request_account()

    connector_type: ConnectorType = request_message.connector_type

    if not connector_type or connector_type == ConnectorType.UNKNOWN:
        return GetConnectorKeysResponse(connector_keys=[])

    connector_keys = ConnectorKey.objects.filter(account=account, connector__connector_type=connector_type,
                                                 is_active=True)
    connector_key_protos = list(x.get_proto() for x in connector_keys)

    return GetConnectorKeysResponse(connector_keys=connector_key_protos)


@web_api(GetConnectorKeysRequest)
def delete_keys(request_message: GetConnectorKeysRequest) -> Union[
    GetConnectorKeysResponse, HttpResponse]:
    account: Account = get_request_account()

    connector_type: ConnectorType = request_message.connector_type

    if not connector_type or connector_type == ConnectorType.UNKNOWN:
        return GetConnectorKeysResponse(message='Connector Type not found')

    ConnectorKey.objects.filter(account=account, connector__connector_type=connector_type, is_active=True).delete()
    return GetConnectorKeysResponse(message='Connector Keys Deleted')


@web_api(SaveConnectorKeysRequest)
def save_keys(request_message: SaveConnectorKeysRequest) -> Union[
    SaveConnectorKeysResponse, HttpResponse]:
    account: Account = get_request_account()

    connector_type: ConnectorType = request_message.connector_type
    connector_keys = request_message.connector_keys

    if not connector_type or connector_type == ConnectorType.UNKNOWN:
        return SaveConnectorKeysResponse(message='Connector Type not found')

    try:
        conn = Connector.objects.get(account=account, connector_type=connector_type, is_active=True)
    except Connector.DoesNotExist:
        conn = Connector.objects.create(account=account, connector_type=connector_type, is_active=True,
                                        metadata={"connector_type": connector_type})

    for conn_key in connector_keys:
        try:
            c_key = ConnectorKey.objects.get(account=account, connector=conn, is_active=True,
                                             key_type=conn_key.key_type)
            c_key.key = conn_key.key.value
            c_key.save()
        except ConnectorKey.DoesNotExist:
            c_key = ConnectorKey.objects.create(account=account, connector=conn, is_active=True,
                                                key_type=conn_key.key_type, key=conn_key.key.value)

    return SaveConnectorKeysResponse(message='Keys saved')


@web_api(EventProcessingFiltersGetRequest)
@use_read_replica
def event_processing_filters_get(request_message: EventProcessingFiltersGetRequest) -> \
        Union[EventProcessingFiltersGetResponse, HttpResponse]:
    try:
        account: Account = get_request_account()
        page = request_message.meta.page
        time_range = request_message.meta.time_range
        if request_message.is_active and not request_message.is_active.value:
            filters = {'is_active': False}
        else:
            filters = {'is_active': True}
        if request_message.event_stream_filter_ids:
            filters['id__in'] = request_message.event_stream_filter_ids

        account_event_processing_filters = account.eventprocessingfilter_set.filter(**filters)
        account_event_processing_filters = filter_page(account_event_processing_filters, page)
        event_processing_filters = list(x.proto for x in account_event_processing_filters)
        for event_processing_filter in event_processing_filters:
            parsed_drd_events = FilterParsedEventData.objects.filter(account_id=account.id,
                                                                     filter_id=event_processing_filter.id.value)
            if time_range:
                parsed_drd_events = filter_time_range(parsed_drd_events, time_range, 'timestamp')
            event_processing_filter.stats.total_generated_drd_event_count.value = parsed_drd_events.count()

        return EventProcessingFiltersGetResponse(success=BoolValue(value=True),
                                                 event_processing_filters=event_processing_filters)
    except Exception as e:
        logger.error(e)
        return EventProcessingFiltersGetResponse(success=BoolValue(value=False),
                                                 message=Message(title='Failed to get event processing filters'))


@web_api(EventProcessingFiltersCreateRequest)
@use_read_replica
def event_processing_filters_create(request_message: EventProcessingFiltersCreateRequest) -> \
        Union[EventProcessingFiltersCreateResponse, HttpResponse]:
    try:
        account: Account = get_request_account()
        if not request_message.event_processing_filter:
            return EventProcessingFiltersCreateResponse(success=BoolValue(value=False),
                                                        message=Message(title='Invalid request',
                                                                        description='No event filter definition found'))

        event_processing_filter = request_message.event_processing_filter
        saved_event_processing_filter = get_or_create_event_processing_filter(account, event_processing_filter)
        if saved_event_processing_filter:
            return EventProcessingFiltersCreateResponse(success=BoolValue(value=True),
                                                        event_processing_filter=saved_event_processing_filter.proto)
    except Exception as e:
        logger.error(e)

    return EventProcessingFiltersCreateResponse(success=BoolValue(value=False),
                                                message=Message(title='Failed to create event processing filter'))


@web_api(EventProcessingFiltersUpdateRequest)
@use_read_replica
def event_processing_filters_update(request_message: EventProcessingFiltersUpdateRequest) -> \
        Union[EventProcessingFiltersUpdateResponse, HttpResponse]:
    try:
        account: Account = get_request_account()
        if not request_message.event_processing_filter_id or not request_message.update_event_processing_filter_ops:
            return EventProcessingFiltersCreateResponse(success=BoolValue(value=False),
                                                        message=Message(title='Invalid request',
                                                                        description='No id or update ops found'))

        account_event_processing_filter = update_or_create_event_processing_filter(account,
                                                                                   request_message.event_processing_filter_id.value,
                                                                                   request_message.update_event_processing_filter_ops)

        if account_event_processing_filter:
            return EventProcessingFiltersUpdateResponse(success=BoolValue(value=True),
                                                        event_processing_filter=account_event_processing_filter.proto)
    except Exception as e:
        logger.error(e)

    return EventProcessingFiltersCreateResponse(success=BoolValue(value=False),
                                                message=Message(title='Failed to update event processing filter'))


@web_api(FilterEventsGetRequest)
@use_read_replica
def event_processing_filters_apply(request_message: FilterEventsGetRequest) -> \
        Union[FilterEventsGetResponse, HttpResponse]:
    try:
        account: Account = get_request_account()
        page = request_message.meta.page
        tr = request_message.meta.time_range
        event_processing_filter: EventProcessingFilterProto = request_message.event_processing_filter
        if not event_processing_filter:
            return FilterEventsGetResponse(success=BoolValue(value=False),
                                           message=Message(title='Invalid request',
                                                           description='No filter definition found'))
        qs = RawEventStreamData.objects.filter(account_id=account.id)
        qs = filter_time_range(qs, tr, 'timestamp')
        all_events_count = qs.count()
        if all_events_count <= 0:
            return FilterEventsGetResponse(success=BoolValue(value=False),
                                           message=Message(title='No events found in the selected time range'))
        qs = filter_page(qs, page, default_limit=5)
        total_event_count = qs.count()
        qs = qs.values('data', 'event_source', 'timestamp')
        event_stream: [StreamEvent] = []
        for q in qs:
            event_timestamp = int(q['timestamp'].timestamp() * 1000)
            event_stream.append(StreamEvent(event=StringValue(value=q['data']), event_source=q['event_source'],
                                            recorded_ingestion_timestamp=event_timestamp))
        filtered_events, un_filtered_events = filter_events(event_processing_filter, event_stream)
        filtered_data_structs = []
        for filtered_data_item in filtered_events:
            s = Struct()
            output = {'created_at': int(filtered_data_item.recorded_ingestion_timestamp),
                      'message': filtered_data_item.event.value}
            s.update(output)
            filtered_data_structs.append(s)
        return FilterEventsGetResponse(meta=get_meta(tr=tr, page=page, total_count=all_events_count),
                                       success=BoolValue(value=True),
                                       stats=EventProcessingFilterProto.Stats(
                                           total_event_count=UInt64Value(value=total_event_count),
                                           total_filtered_event_count=UInt64Value(value=len(filtered_events)),
                                           total_filtered_failed_event_count=UInt64Value(
                                               value=len(un_filtered_events))),
                                       filtered_events=filtered_data_structs)
    except Exception as e:
        logger.error(e)
        return FilterEventsGetResponse(success=BoolValue(value=False),
                                       message=Message(title='Failed to get event processing filters'))


@web_api(EventProcessingParsersGetRequest)
@use_read_replica
def event_processing_parsers_get(request_message: EventProcessingParsersGetRequest) -> \
        Union[EventProcessingParsersGetResponse, HttpResponse]:
    try:
        account: Account = get_request_account()
        page = request_message.meta.page
        tr: TimeRange = request_message.meta.time_range
        if request_message.is_active and not request_message.is_active.value:
            filters = {'is_active': False}
        else:
            filters = {'is_active': True}
        if request_message.event_stream_filter_id and request_message.event_stream_filter_id.value:
            filters['filter_id'] = request_message.event_stream_filter_id.value
        if request_message.event_stream_parser_ids:
            filters['id__in'] = request_message.event_stream_parser_ids

        account_event_processing_parsers = account.eventprocessingparser_set.filter(**filters)
        all_parser_count = account_event_processing_parsers.count()
        account_event_processing_parsers = filter_page(account_event_processing_parsers, page)
        event_processing_parsers = list(x.proto for x in account_event_processing_parsers)
        for parser in event_processing_parsers:
            parsed_drd_events = FilterParsedEventData.objects.filter(account_id=account.id, parser_id=parser.id.value)
            if tr is not None and tr:
                parsed_drd_events = filter_time_range(parsed_drd_events, tr, 'timestamp')
            parser.stats.total_generated_drd_event_count.value = parsed_drd_events.count()

        return EventProcessingParsersGetResponse(meta=get_meta(tr=tr, page=page, total_count=all_parser_count),
                                                 success=BoolValue(value=True),
                                                 event_processing_parsers=event_processing_parsers)
    except Exception as e:
        logger.error(e)
        return EventProcessingParsersGetResponse(success=BoolValue(value=False),
                                                 message=Message(title='Failed to get event processing parsers'))


@web_api(EventProcessingParsersCreateRequest)
@use_read_replica
def event_processing_parsers_create(request_message: EventProcessingParsersCreateRequest) -> \
        Union[EventProcessingParsersCreateResponse, HttpResponse]:
    try:
        account: Account = get_request_account()
        if not request_message.event_processing_parsers:
            return EventProcessingParsersCreateResponse(success=BoolValue(value=False),
                                                        message=Message(title='Invalid request',
                                                                        description='No event parser definitions found'))

        event_processing_parsers: [EventProcessingParserProto] = request_message.event_processing_parsers
        saved_event_processing_parsers = get_or_create_event_processing_parser(account, event_processing_parsers)
        if saved_event_processing_parsers:
            saved_event_processing_parser_protos = list(x.proto for x in saved_event_processing_parsers)
            return EventProcessingParsersCreateResponse(success=BoolValue(value=True),
                                                        event_processing_parsers=saved_event_processing_parser_protos)
    except Exception as e:
        logger.error(e)
    return EventProcessingParsersCreateResponse(success=BoolValue(value=False),
                                                message=Message(title='Failed to create event processing parsers'))


@web_api(EventProcessingParsersUpdateRequest)
@use_read_replica
def event_processing_parsers_update(request_message: EventProcessingParsersUpdateRequest) -> \
        Union[EventProcessingParsersUpdateResponse, HttpResponse]:
    try:
        account: Account = get_request_account()
        if not request_message.event_processing_parser_id or not request_message.update_event_processing_parser_ops:
            return EventProcessingParsersUpdateResponse(success=BoolValue(value=False),
                                                        message=Message(title='Invalid request',
                                                                        description='No id or update ops found'))

        account_event_processing_parser = update_or_create_event_processing_parser(account,
                                                                                   request_message.event_processing_parser_id.value,
                                                                                   request_message.update_event_processing_parser_ops)

        if account_event_processing_parser:
            return EventProcessingParsersUpdateResponse(success=BoolValue(value=True),
                                                        event_processing_parser=account_event_processing_parser.proto)
    except Exception as e:
        logger.error(e)

    return EventProcessingParsersUpdateResponse(success=BoolValue(value=False),
                                                message=Message(title='Failed to update event processing filter'))


@web_api(ParseFilteredEventsGetRequest)
@use_read_replica
def event_processing_parsers_apply_parser(request_message: ParseFilteredEventsGetRequest) -> \
        Union[ParseFilteredEventsGetResponse, HttpResponse]:
    try:
        event_processing_parser: EventProcessingParserProto = request_message.event_processing_parser
        events = request_message.events
        if not event_processing_parser:
            return ParseFilteredEventsGetResponse(success=BoolValue(value=False),
                                                  message=Message(title='Invalid request',
                                                                  description='No parser definition found'))

        if not events:
            return ParseFilteredEventsGetResponse(success=BoolValue(value=False),
                                                  message=Message(title='Invalid request',
                                                                  description='No events found'))
        parsed_event_jsons, parser_failed_events_list = parse_events(event_processing_parser, events)
        parsed_event_structs = []
        parsed_keys_count = {}
        timestamp_keys = []
        for parsed_event_json in parsed_event_jsons:
            s = Struct()
            s.update(parsed_event_json)
            parsed_event_structs.append(s)
            for k, v in parsed_event_json.items():
                if isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
                    if k in parsed_keys_count:
                        parsed_keys_count[k] += 1
                    else:
                        parsed_keys_count[k] = 1
                    if find_datetime_format_and_convert(v) is not None:
                        if k == '$drd_recorded_ingestion_timestamp':
                            continue
                        timestamp_keys.append(k)
        if parsed_keys_count:
            parsed_keys_count.pop('$drd_recorded_ingestion_timestamp', None)
            parsed_keys_count.pop('$drd_recorded_event_source', None)
        stats: EventProcessingParserProto.Stats = EventProcessingParserProto.Stats(
            total_parsed_event_count=UInt64Value(value=len(parsed_event_structs)),
            total_parser_failed_event_count=UInt64Value(value=len(parser_failed_events_list)),
            total_parsed_event_keys=UInt64Value(value=len(parsed_keys_count.keys())),
            parsed_event_keys=list(parsed_keys_count.keys()),
            parsed_timestamp_keys=timestamp_keys
        )
        parser_failed_event_str_list = []
        for e in parser_failed_events_list:
            parser_failed_event_str_list.append(e.event.value)
        return ParseFilteredEventsGetResponse(success=BoolValue(value=True),
                                              parsed_events=parsed_event_structs,
                                              parser_failed_events=parser_failed_event_str_list,
                                              stats=stats)
    except Exception as e:
        logger.error(e)
        return ParseFilteredEventsGetResponse(success=BoolValue(value=False),
                                              message=Message(title='Failed to get event processing parsers'))


@web_api(GenerateDRDParsedEventsGetRequest)
@use_read_replica
def event_processing_parsers_apply_drd_event_definition_rule(request_message: GenerateDRDParsedEventsGetRequest) -> \
        Union[GenerateDRDParsedEventsGetResponse, HttpResponse]:
    try:
        account: Account = get_request_account()
        drd_event_definition_rule: EventProcessingParserProto.ParsedDrdEventDefinition = \
            request_message.drd_event_definition_rule
        if not drd_event_definition_rule:
            return GenerateDRDParsedEventsGetResponse(success=BoolValue(value=False),
                                                      message=Message(title='Invalid request',
                                                                      description='No Drd Event definition found'))

        parsed_events = request_message.parsed_events
        if not parsed_events:
            return GenerateDRDParsedEventsGetResponse(success=BoolValue(value=False),
                                                      message=Message(title='Invalid request',
                                                                      description='No events found'))
        drd_events, drd_event_definition_failed_event_jsons = generated_drd_events_from_parsed_event_string(
            account.id, drd_event_definition_rule, parsed_events)
        generated_drd_events: [IngestionEvent] = [event.event for event in drd_events]
        return GenerateDRDParsedEventsGetResponse(success=BoolValue(value=True),
                                                  generated_drd_events=generated_drd_events,
                                                  drd_event_definition_failed_events=drd_event_definition_failed_event_jsons)
    except Exception as e:
        logger.error(e)
        return ParseFilteredEventsGetResponse(success=BoolValue(value=False),
                                              message=Message(title='Failed to get event processing parsers'))


@web_api(EventProcessingFiltersParsersCreateRequest)
@use_read_replica
def event_processing_filters_parsers_create(request_message: EventProcessingFiltersParsersCreateRequest) -> \
        Union[EventProcessingFiltersParsersCreateResponse, HttpResponse]:
    try:
        account: Account = get_request_account()
        if not request_message.event_processing_parsers:
            return EventProcessingFiltersParsersCreateResponse(success=BoolValue(value=False),
                                                               message=Message(title='Invalid request',
                                                                               description='No event parser definitions found'))

        event_processing_parsers: [EventProcessingParserProto] = request_message.event_processing_parsers
        saved_event_processing_parsers = get_or_create_event_processing_filter_parsers(account,
                                                                                       event_processing_parsers)
        if saved_event_processing_parsers:
            saved_event_processing_parser_protos = list(x.proto for x in saved_event_processing_parsers)
            return EventProcessingFiltersParsersCreateResponse(success=BoolValue(value=True),
                                                               event_processing_parsers=saved_event_processing_parser_protos)
    except Exception as e:
        logger.error(e)
    return EventProcessingParsersCreateResponse(success=BoolValue(value=False),
                                                message=Message(title='Failed to create event processing parsers'))
