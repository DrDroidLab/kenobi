import abc
import json
import re
from json import JSONDecodeError
from typing import List, Dict

from protos.event.stream_processing_pb2 import EventProcessingFilter, RegexEventProcessingFilter, \
    JSONEventProcessingFilter
from protos.kafka.event_stream_pb2 import StreamEvent
from utils.proto_utils import dict_to_proto, proto_to_dict


class EventFilterEngine(abc.ABC):
    filter_type: EventProcessingFilter.Type

    @abc.abstractmethod
    def filter(self, filter_config: dict, event_stream: [StreamEvent]) -> (List, List):
        pass


class DefaultEventFilterEngine(EventFilterEngine):
    filter_type: EventProcessingFilter.Type = EventProcessingFilter.Type.DEFAULT

    def filter(self, filter_config, event_stream: [StreamEvent]) -> (List, List):
        return event_stream, []


class RegexEventFilterEngine(EventFilterEngine):
    filter_type: EventProcessingFilter.Type = EventProcessingFilter.Type.REGEX

    def filter(self, filter_config, event_stream: [StreamEvent]) -> (List, List):
        if not filter_config:
            raise Exception("Filter config not found")
        regex_filter: RegexEventProcessingFilter = dict_to_proto(filter_config, RegexEventProcessingFilter)
        if not regex_filter:
            raise Exception("Regex filter not found in filter config")
        regex_list = []
        for regex_str in regex_filter.regular_expressions:
            regex_list.append(re.compile(regex_str))
        filtered_events: [StreamEvent] = []
        un_filtered_events: [StreamEvent] = []
        for e in event_stream:
            if all(re.search(pattern, e.event.value) for pattern in regex_list):
                filtered_events.append(e)
            else:
                un_filtered_events.append(e)
        return filtered_events, un_filtered_events


class JSONEventFieldFilterEngine(EventFilterEngine):
    filter_type: EventProcessingFilter.Type = EventProcessingFilter.Type.JSON_FIELD

    def filter(self, filter_config, event_stream: [StreamEvent]) -> (List, List):
        if not filter_config:
            raise Exception("Filter config not found")
        json_field_filter: JSONEventProcessingFilter = dict_to_proto(filter_config, JSONEventProcessingFilter)
        if not json_field_filter:
            raise Exception("JSON field filter not found in filter config")
        filters: [JSONEventProcessingFilter.JSONFilter] = json_field_filter.filters
        filtered_events: [StreamEvent] = []
        un_filtered_events: [StreamEvent] = []
        for e in event_stream:
            if e.type is None or e.type != StreamEvent.Type.JSON:
                un_filtered_events.append(e)
                continue
            try:
                event_json = json.loads(e.event.value)
                for key_filter in filters:
                    value = event_json.get(key_filter.key, None)
                    if value is None:
                        continue
                    elif str(value) == key_filter.literal.string:
                        filtered_events.append(e)
                    else:
                        un_filtered_events.append(e)
            except JSONDecodeError:
                un_filtered_events.append(e)
        return filtered_events, un_filtered_events


class EventStreamProcessingFilterFacade:

    def __init__(self):
        self._map = {}

    def register(self, filter_type: EventProcessingFilter.Type, filter_engine: EventFilterEngine):
        self._map[filter_type] = filter_engine

    def filter_event_stream(self, scope, event_stream: [StreamEvent]) -> (Dict, List):
        filter_stream_map = {}
        event_processing_filters = scope.eventprocessingfilter_set.filter(is_active=True)
        all_filtered_events = []
        for event_filter in event_processing_filters:
            filter_engine = self._map[event_filter.type]
            if filter_engine:
                filtered_events, _ = filter_engine.filter(event_filter.filter, event_stream)
                if filtered_events:
                    filter_stream_map[event_filter.id] = filtered_events
                    all_filtered_events.extend(filtered_events)
            else:
                print(f"Filter engine not found for filter type: {event_filter.filter_type}")
        all_unfiltered_event_list = []
        for event in event_stream:
            if event not in all_filtered_events:
                all_unfiltered_event_list.append(event)
        return filter_stream_map, all_unfiltered_event_list

    def filter_events(self, event_processing_filter: EventProcessingFilter, events: [StreamEvent]) -> (List, List):
        if not event_processing_filter:
            raise Exception("Event processing filter not found")
        filter_engine = self._map[event_processing_filter.type]
        if event_processing_filter.type == EventProcessingFilter.Type.DEFAULT:
            return events, []
        elif event_processing_filter.type == EventProcessingFilter.Type.REGEX and event_processing_filter.regex:
            filter_config = proto_to_dict(event_processing_filter.regex)
            if filter_engine and filter_config:
                return filter_engine.filter(filter_config, events)
            else:
                print("Filter Engine/Config not found")
        else:
            print(f"Filter engine not found for filter type: {event_processing_filter.type}")
        return [], []


stream_event_processing_filter_facade = EventStreamProcessingFilterFacade()
stream_event_processing_filter_facade.register(EventProcessingFilter.Type.DEFAULT, DefaultEventFilterEngine())
stream_event_processing_filter_facade.register(EventProcessingFilter.Type.REGEX, RegexEventFilterEngine())


def filter_event_stream(scope, event_stream: [StreamEvent]):
    return stream_event_processing_filter_facade.filter_event_stream(scope, event_stream)


def filter_events(event_processing_filter: EventProcessingFilter, event_stream: [StreamEvent]):
    return stream_event_processing_filter_facade.filter_events(event_processing_filter, event_stream)