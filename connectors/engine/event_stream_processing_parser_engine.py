import abc
import json
import logging
from json import JSONDecodeError
from typing import List, Dict

from google.protobuf.wrappers_pb2 import StringValue, UInt64Value
from google.protobuf import json_format
from pygrok import Grok

from connectors.utils import find_datetime_format_and_convert
from event.clickhouse.model_helper import ingest_account_drd_event_definition_failed_parsed_events, get_data_type, \
    ingest_account_filter_parsed_events
from protos.event.base_pb2 import Event as EventProto
from protos.event.stream_processing_pb2 import EventProcessingParser, GrokEventProcessingParser
from protos.kafka.event_stream_pb2 import StreamEvent
from protos.kafka.raw_events_pb2 import RawEventPayloadValue
from prototype.utils.utils import current_milli_time, transform_event_json
from utils.proto_utils import dict_to_proto, proto_to_dict

logger = logging.getLogger(__name__)


def value_infer_type(event_value):
    if not event_value:
        return None
    if isinstance(event_value, str) and event_value.lower() == "true":
        return True
    elif isinstance(event_value, str) and event_value.lower() == "false":
        return False
    else:
        try:
            num = int(event_value)
            return num
        except ValueError:
            try:
                num = float(event_value)
                return num
            except ValueError:
                return event_value


def list_infer_type(event_list: []):
    for i, v in enumerate(event_list):
        if isinstance(v, dict):
            event_list[i] = dict_infer_type(v)
        elif isinstance(v, list):
            event_list[i] = list_infer_type(v)
        else:
            event_list[i] = value_infer_type(v)
    return event_list


def dict_infer_type(event_json_dict: dict):
    for k, v in event_json_dict.items():
        if isinstance(v, dict):
            event_json_dict[k] = dict_infer_type(v)
        elif isinstance(v, list):
            event_json_dict[k] = list_infer_type(v)
        else:
            event_json_dict[k] = value_infer_type(v)
    return event_json_dict


def generate_drd_event(account_id, drd_event_definition: dict, event_jsons: []) -> (List, List):
    try:
        drd_events: [RawEventPayloadValue] = []
        drd_event_definition_failed_event_jsons = []
        if not drd_event_definition:
            raise Exception("DRD event definition not found")
        drd_event_definition_rule: EventProcessingParser.ParsedDrdEventDefinition = dict_to_proto(
            drd_event_definition,
            EventProcessingParser.ParsedDrdEventDefinition)
        timestamp_field = None
        if drd_event_definition_rule.event_timestamp_field and drd_event_definition_rule.event_timestamp_field.value:
            timestamp_field = drd_event_definition_rule.event_timestamp_field.value
        event_name_field = None
        custom_event_name = None
        which_one_of = drd_event_definition_rule.WhichOneof('event_name')
        if which_one_of == 'event_name_field':
            event_name_field = drd_event_definition_rule.event_name_field.value
        elif which_one_of == 'custom_event_name':
            custom_event_name = drd_event_definition_rule.custom_event_name.value
        else:
            raise Exception("Event type rule not found in drd event definition")
        for event in event_jsons:
            if not event or not isinstance(event, dict):
                print(
                    f"Parsed Event is not a valid JSON. Skipping Generating DRD Event: {event} for account_id: "
                    f"{account_id}")
                continue
            drd_event_json = {}
            processed_kvs = {}
            for k, v in event.items():
                if event_name_field is not None and event_name_field == k:
                    drd_event_json['name'] = v
                elif timestamp_field is not None and timestamp_field == k:
                    drd_event_json['timestamp'] = find_datetime_format_and_convert(v)
                else:
                    processed_kvs[k] = v
            if 'name' not in drd_event_json:
                if custom_event_name is not None:
                    drd_event_json['name'] = custom_event_name
                else:
                    drd_event_definition_failed_event_jsons.append(event)
            if 'timestamp' not in drd_event_json:
                drd_event_json['timestamp'] = int(processed_kvs.get('$drd_recorded_ingestion_timestamp',
                                                                    current_milli_time()))
            event_source = int(processed_kvs.pop('$drd_recorded_event_source', EventProto.EventSource.UNKNOWN))
            drd_event_json['payload'] = processed_kvs
            ingestion_event = transform_event_json(drd_event_json)
            raw_event_payload_value: RawEventPayloadValue = RawEventPayloadValue(
                account_id=UInt64Value(value=account_id),
                event=ingestion_event,
                event_source=event_source
            )
            drd_events.append(raw_event_payload_value)
        return drd_events, drd_event_definition_failed_event_jsons
    except Exception as e:
        logger.error(f"Error generating DRD event: {e}")
        return [], []


class EventParsingEngine(abc.ABC):
    parser_type: EventProcessingParser.Type

    @abc.abstractmethod
    def parse(self, parser_config: dict, event_stream: [StreamEvent]) -> (List, List):
        pass


class DefaultEventParsingEngine(EventParsingEngine):
    parser_type: EventProcessingParser.Type = EventProcessingParser.Type.DEFAULT

    def parse(self, parser_config, event_stream: [StreamEvent]) -> (List, List):
        parsed_events = []
        parser_failed_events: [StreamEvent] = []
        for e in event_stream:
            if e.type != StreamEvent.Type.JSON:
                parser_failed_events.append(e)
                continue
            event_value = e.event.value
            try:
                generated_event_dict = json.loads(event_value)
                if e.event_source:
                    event_source = e.event_source
                else:
                    event_source = EventProto.EventSource.API
                if e.recorded_ingestion_timestamp:
                    recorded_ingestion_timestamp = e.recorded_ingestion_timestamp
                else:
                    recorded_ingestion_timestamp = current_milli_time()
                generated_event_dict['$drd_raw_event_id'] = e.uuid_str.value
                generated_event_dict['$drd_recorded_event_source'] = event_source
                generated_event_dict['$drd_recorded_ingestion_timestamp'] = recorded_ingestion_timestamp
                generated_event_dict = dict_infer_type(generated_event_dict)
                parsed_events.append(generated_event_dict)
            except JSONDecodeError:
                parser_failed_events.append(e)
        return parsed_events, parser_failed_events


class GrokEventParsingEngine(EventParsingEngine):
    parser_type: EventProcessingParser.Type = EventProcessingParser.Type.GROK

    def parse(self, parser_config, event_stream: [StreamEvent]) -> (List, List):
        if not parser_config:
            raise Exception("Parser config not found")
        grok_parser: GrokEventProcessingParser = dict_to_proto(parser_config, GrokEventProcessingParser)
        if not grok_parser or not grok_parser.grok_expression:
            raise Exception("Grok parser/expression not found in filter config")
        grok_expression = grok_parser.grok_expression.value
        grok_rule = Grok(grok_expression)
        parsed_events = []
        parser_failed_events: [StreamEvent] = []
        for e in event_stream:
            event_value = e.event.value
            if e.event_source:
                event_source = e.event_source
            else:
                event_source = EventProto.EventSource.API
            if e.recorded_ingestion_timestamp:
                recorded_ingestion_timestamp = e.recorded_ingestion_timestamp
            else:
                recorded_ingestion_timestamp = current_milli_time()
            if grok_rule.match(e.event.value):
                generated_event_dict = grok_rule.match(event_value)
                generated_event_dict['$drd_recorded_event_source'] = event_source
                generated_event_dict['$drd_recorded_ingestion_timestamp'] = recorded_ingestion_timestamp
                generated_event_dict = dict_infer_type(generated_event_dict)
                parsed_events.append(generated_event_dict)
            else:
                parser_failed_events.append(e)
        return parsed_events, parser_failed_events


class EventProcessingParsingFacade:

    def __init__(self):
        self._map = {}

    def register(self, parser_type: EventProcessingParser.Type, parser_engine: EventParsingEngine):
        self._map[parser_type] = parser_engine

    def parse_filtered_event_stream(self, scope, filter_stream_map: Dict) -> (List, Dict):
        parsed_drd_events_list = []
        drd_definition_failed_events_map = {}
        parser_failed_filter_map = {}
        try:
            for filter_id, event_stream in filter_stream_map.items():
                parsed_event_map = {}
                parser_failed_event_list = []
                event_processing_filter_parsers = scope.eventprocessingparser_set.filter(is_active=True).filter(
                    filter_id=filter_id)
                for event_parser in event_processing_filter_parsers:
                    parser_engine = self._map[event_parser.type]
                    if parser_engine:
                        parsed_events, parser_failed_events = parser_engine.parse(event_parser.parser, event_stream)
                        if parsed_events:
                            drd_events, drd_event_definition_failed_event_jsons = generate_drd_event(
                                scope.id, event_parser.drd_event_definition_rule, parsed_events)
                            if drd_events:
                                parsed_event_list = parsed_event_map.get(event_parser.id, [])
                                parsed_event_list.extend(drd_events)
                                parsed_event_map[event_parser.id] = parsed_event_list
                                parsed_drd_events_list.extend(drd_events)
                            if drd_event_definition_failed_event_jsons:
                                drd_definition_failed_events_list = drd_definition_failed_events_map.get(
                                    event_parser.id, [])
                                drd_definition_failed_events_list.extend(drd_event_definition_failed_event_jsons)
                                drd_definition_failed_events_map[event_parser.id] = drd_definition_failed_events_list
                    else:
                        print(f"Parser engine not found for parser type: {event_parser.parser_type}")
                        parser_failed_events = event_stream
                    parser_failed_event_list.extend(parser_failed_events)
                parser_failed_event_list_set = []
                for event in parser_failed_event_list:
                    if event not in parser_failed_event_list_set:
                        parser_failed_event_list_set.append(event)
                parser_failed_filter_map[filter_id] = parser_failed_event_list_set
                ingest_account_filter_parsed_events(scope.id, filter_id, parsed_event_map)
        except Exception as e:
            logger.error(f"Error parsing filtered event stream: {e}")
            pass
        ingest_account_drd_event_definition_failed_parsed_events(scope.id, drd_definition_failed_events_map)
        return parsed_drd_events_list, parser_failed_filter_map

    def parse_event_stream(self, event_processing_parser: EventProcessingParser,
                           event_stream: [StreamEvent]) -> (List, List):
        if not event_processing_parser:
            raise Exception("Event processing parser not found")
        parser_engine = self._map[event_processing_parser.type]
        if event_processing_parser.type == EventProcessingParser.Type.DEFAULT:
            if parser_engine:
                return parser_engine.parse(None, event_stream)
            else:
                print("Parser Engine not found")
        elif event_processing_parser.type == EventProcessingParser.Type.GROK and event_processing_parser.grok_parser:
            parser_config = proto_to_dict(event_processing_parser.grok_parser)
            if parser_engine and parser_config:
                return parser_engine.parse(parser_config, event_stream)
            else:
                print("Parser Engine/Config not found")
        else:
            print("Parser Type/Definition not found")
        return [], []


stream_event_processing_parser_facade = EventProcessingParsingFacade()
stream_event_processing_parser_facade.register(EventProcessingParser.Type.DEFAULT, DefaultEventParsingEngine())
stream_event_processing_parser_facade.register(EventProcessingParser.Type.GROK, GrokEventParsingEngine())


def parse_filtered_event_stream(scope, filter_stream_map: Dict) -> (List, Dict):
    return stream_event_processing_parser_facade.parse_filtered_event_stream(scope, filter_stream_map)


def parse_events(event_processing_parser: EventProcessingParser, events) -> (List, List):
    event_stream: [StreamEvent] = []
    for e in events:
        data_type = get_data_type(e)
        event_stream.append(StreamEvent(event=StringValue(value=e), type=data_type))
    return stream_event_processing_parser_facade.parse_event_stream(event_processing_parser, event_stream)


def generated_drd_events_from_parsed_event_string(account_id,
                                                  drd_event_definition_rule: EventProcessingParser.ParsedDrdEventDefinition,
                                                  parsed_events) -> (List, List):
    if not drd_event_definition_rule:
        raise Exception("DRD Event Definition Rule not found")
    drd_event_definition_rule = proto_to_dict(drd_event_definition_rule)
    parsed_event_jsons = []
    for event in parsed_events:
        try:
            parsed_event_json = json_format.MessageToDict(event)
            parsed_event_jsons.append(parsed_event_json)
        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            pass
    return generate_drd_event(account_id, drd_event_definition_rule, parsed_event_jsons)
