from django.utils.functional import cached_property

from clickhouse_backend import models as clickhouse_models
import json

from event.models import EventType
from protos.event.base_pb2 import Event as EventProto


def clean_event_kvs(event_kvs: list):
    for kvs in event_kvs:
        if kvs.get('value').get('string_value'):
            kvs['value']['string_value'] = str(kvs.get('value')['string_value'])
        if kvs.get('value').get('int_value'):
            kvs['value']['int_value'] = int(kvs.get('value')['int_value'])
        if kvs.get('bool_value'):
            kvs['value']['bool_value'] = bool(kvs.get('value')['bool_value'])
        if kvs.get('double_value'):
            kvs['value']['double_value'] = float(kvs.get('value')['double_value'])
        if kvs.get('array_value'):
            kvs['value']['string_value'] = json.dumps(kvs.get('value')['array_value']['values'])
    return event_kvs


class Events(clickhouse_models.ClickhouseModel):
    id = clickhouse_models.UInt64Field(primary_key=True)
    account_id = clickhouse_models.UInt64Field()
    created_at = clickhouse_models.DateTime64Field()
    timestamp = clickhouse_models.DateTime64Field()
    event_type_id = clickhouse_models.UInt16Field()
    event_type_name = clickhouse_models.StringField()
    event_source = clickhouse_models.UInt16Field()
    processed_kvs = clickhouse_models.JSONField()
    ingested_event = clickhouse_models.StringField()

    class Meta:
        db_table = 'events'

    @cached_property
    def proto(self):
        try:
            kvs_json = json.loads(self.ingested_event)
        except:
            kvs_json = {}

        kvs_list = clean_event_kvs(kvs_json.get('kvs', []))
        proto = EventProto(
            id=int(self.id), event_type=EventType.proto_partial_from_sql(int(self.event_type_id), self.event_type_name),
            kvs=kvs_list,
            timestamp=int(self.timestamp.timestamp()),
            event_source=EventProto.EventSource.API
        )
        return proto


class MonitorTransactions(clickhouse_models.ClickhouseModel):
    id = clickhouse_models.UInt64Field(primary_key=True)
    account_id = clickhouse_models.UInt64Field()
    monitor_id = clickhouse_models.UInt64Field()
    transaction = clickhouse_models.StringField()
    status = clickhouse_models.UInt16Field()
    transaction_time = clickhouse_models.Float64Field()

    event_id = clickhouse_models.UInt64Field()
    monitor_transaction_event_type = clickhouse_models.UInt16Field()
    event_type_id = clickhouse_models.UInt64Field()
    event_type_name = clickhouse_models.StringField()
    event_timestamp = clickhouse_models.DateTime64Field()
    event_source = clickhouse_models.UInt16Field()
    event_processed_kvs = clickhouse_models.JSONField()
    ingested_event = clickhouse_models.StringField()

    created_at = clickhouse_models.DateTime64Field()

    class Meta:
        db_table = 'monitor_transactions'


class RawEventStreamData(clickhouse_models.ClickhouseModel):
    id = clickhouse_models.UUIDField(primary_key=True)
    account_id = clickhouse_models.UInt64Field()
    created_at = clickhouse_models.DateTime64Field()
    timestamp = clickhouse_models.DateTime64Field()
    event_source = clickhouse_models.UInt16Field()
    data = clickhouse_models.StringField()
    type = clickhouse_models.UInt16Field()

    class Meta:
        db_table = 'raw_event_stream_data'


class FilterFailedRawEventStreamData(clickhouse_models.ClickhouseModel):
    id = clickhouse_models.UUIDField(primary_key=True)
    account_id = clickhouse_models.UInt64Field()
    created_at = clickhouse_models.DateTime64Field()
    timestamp = clickhouse_models.DateTime64Field()
    event_source = clickhouse_models.UInt16Field()
    data = clickhouse_models.StringField()
    type = clickhouse_models.UInt16Field()

    class Meta:
        db_table = 'filter_failed_raw_event_stream_data'


class ParserFailedRawEventStreamData(clickhouse_models.ClickhouseModel):
    id = clickhouse_models.UUIDField(primary_key=True)
    account_id = clickhouse_models.UInt64Field()
    filter_id = clickhouse_models.UInt64Field()
    created_at = clickhouse_models.DateTime64Field()
    timestamp = clickhouse_models.DateTime64Field()
    event_source = clickhouse_models.UInt16Field()
    filtered_event_data = clickhouse_models.StringField()

    class Meta:
        db_table = 'parser_failed_raw_event_stream_data'


class DrdEventDefinitionFailedParsedEventData(clickhouse_models.ClickhouseModel):
    id = clickhouse_models.UUIDField(primary_key=True)
    account_id = clickhouse_models.UInt64Field()
    parser_id = clickhouse_models.UInt64Field()
    created_at = clickhouse_models.DateTime64Field()
    timestamp = clickhouse_models.DateTime64Field()
    event_source = clickhouse_models.UInt16Field()
    parsed_event = clickhouse_models.StringField()

    class Meta:
        db_table = 'drd_event_definition_failed_parsed_event_data'


class FilterParsedEventData(clickhouse_models.ClickhouseModel):
    id = clickhouse_models.UUIDField(primary_key=True)
    account_id = clickhouse_models.UInt64Field()
    filter_id = clickhouse_models.UInt64Field()
    parser_id = clickhouse_models.UInt64Field()
    created_at = clickhouse_models.DateTime64Field()
    timestamp = clickhouse_models.DateTime64Field()
    event_source = clickhouse_models.UInt16Field()
    parsed_drd_event = clickhouse_models.StringField()

    class Meta:
        db_table = 'filter_parsed_event_data'
