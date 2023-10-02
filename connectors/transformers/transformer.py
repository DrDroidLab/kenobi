import ast
import json
import logging
import re
from typing import List

from django.conf import settings
from sentry_sdk import capture_exception

from connectors.models import TransformerMapping
from connectors.transformers.decoder import decoder_facade
from protos.event.connectors_pb2 import TransformerType, DecoderType
from prototype.utils.utils import current_milli_time


class TransformerFacadeException(ValueError):
    pass


logger = logging.getLogger(__name__)


class Transformer:
    type: TransformerType = None

    @classmethod
    def transform(cls, input_schema):
        pass


class SegmentDefaultTransformer(Transformer):

    def __init__(self):
        self.type = TransformerType.SEGMENT_DFAULT_TRANSFORMER

    @classmethod
    def transform(cls, input_schema) -> List:
        event = {}
        payload = {}

        if input_schema['type'] == 'track':
            event["name"] = input_schema.pop('event', None)
            payload['type'] = input_schema.pop('type', None)
            payload.update(input_schema['properties'])
            payload['userId'] = input_schema.pop('userId', None)
            event["payload"] = payload
        elif input_schema['type'] == 'page':
            event["name"] = input_schema.pop('name', None)
            payload['type'] = input_schema.pop('type', None)
            payload.update(input_schema['properties'])
            payload['userId'] = input_schema.pop('userId', None)
            event["payload"] = payload
        elif input_schema['type'] == 'screen':
            event["name"] = input_schema.pop('name', None)
            payload['type'] = input_schema.pop('type', None)
            payload.update(input_schema['properties'])
            event["payload"] = payload
        elif input_schema['type'] == 'group':
            event["name"] = input_schema.pop('type', None)
            payload['groupId'] = input_schema.pop('groupId', None)
            payload['userId'] = input_schema.pop('userId', None)
            traits = input_schema.pop('traits', None)
            if traits:
                payload.update(traits)
            event["payload"] = payload
        elif input_schema['type'] == 'identify':
            event["name"] = input_schema.pop('type', None)
            payload['userId'] = input_schema.pop('userId', None)
            traits = input_schema.pop('traits', None)
            if traits:
                payload.update(traits)
            event["payload"] = payload
        elif input_schema['type'] == 'alias':
            event["name"] = input_schema.pop('type', None)
            payload['previousId'] = input_schema.pop('previousId', None)
            payload['userId'] = input_schema.pop('userId', None)
            event["payload"] = payload

        if not event:
            raise TransformerFacadeException("Invalid Input Schema")

        return [event]


class AmplitudeDefaultTransformer(Transformer):

    def __init__(self):
        self.type = TransformerType.AMPLITUDE_DEFAULT_TRANSFORMER

    @classmethod
    def transform(cls, input_schema) -> List:
        event = {"name": input_schema.pop('event_type', None), "payload": input_schema}
        return [event]


class CloudwatchJsonLogTransformer(Transformer):

    def __init__(self):
        self.type = TransformerType.CLOUDWATCH_JSON_LOG_TRANSFORMER

    @classmethod
    def transform(cls, input_schema) -> List:
        events = []
        message_type = input_schema.get('messageType', None)
        if message_type and message_type == 'DATA_MESSAGE':
            log_events = input_schema.get('logEvents', None)
            if log_events:
                for log in log_events:
                    try:
                        log_message = log.get('message', None)
                        time_millis = log.get('timestamp', current_milli_time())
                        if log_message:
                            cleaned_log = json.loads(log_message)
                            if cleaned_log:
                                event_dict = cleaned_log
                                if event_dict and event_dict.get('msg', None) is not None:
                                    event_time = event_dict.pop('event_time', time_millis)
                                    event = {"name": event_dict.get('event_name', "").replace(" ", "_"), "payload": event_dict,
                                             "timestamp": event_time}
                                    events.append(event)

                    except Exception as e:
                        capture_exception(e)
                        logger.error(
                            "Exception generating event for Cloudwatch JSON Log: {}, error: {}".format(log, e))
                        continue

        if not events:
            logger.error("No events generated for Cloudwatch JSON Logs: {}".format(input_schema))
        return events


class TransformerFacade:

    def __init__(self):
        self._map = {}

    def register(self, transformer_type: TransformerType, transformer: Transformer):
        self._map[transformer_type] = transformer

    def transform(self, transformer_mapping: TransformerMapping, message):

        decoder_type: DecoderType = transformer_mapping.decoder_type
        if not decoder_type:
            raise TransformerFacadeException(f'No decoder found with type {decoder_type}')

        transformer_type: TransformerType = transformer_mapping.transformer_type
        if not transformer_type:
            raise TransformerFacadeException(f'No transformer found with type {decoder_type}')

        if not transformer_mapping.is_active:
            raise TransformerFacadeException(f'In active transformer mapping found with id {transformer_mapping.id}')

        decoded_message = decoder_facade.decode(decoder_type, message)
        return self._map[transformer_type].transform(decoded_message)


transformer_facade = TransformerFacade()
transformer_facade.register(TransformerType.SEGMENT_DFAULT_TRANSFORMER, SegmentDefaultTransformer())
transformer_facade.register(TransformerType.AMPLITUDE_DEFAULT_TRANSFORMER, AmplitudeDefaultTransformer())
transformer_facade.register(TransformerType.CLOUDWATCH_JSON_LOG_TRANSFORMER, CloudwatchJsonLogTransformer())
