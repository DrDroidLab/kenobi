import base64
import gzip
import json
import logging
from json import JSONDecodeError
from typing import Dict, List

from protos.event.base_pb2 import Event as EventProto
from protos.event.connectors_pb2 import DecoderType
from protos.event.schema_pb2 import AWSKinesisEventPayload, DrdCollectorEventPayload

logger = logging.getLogger(__name__)


class SourceDecoder:
    decoder_type: DecoderType = None

    @classmethod
    def decode(cls, message):
        pass


class DefaultDecoder(SourceDecoder):

    def __init__(self):
        self.decoder = DecoderType.UNKNOWN_DT

    @classmethod
    def decode(cls, message):
        return message


class AWSKinesisFirehoseRecordDecoder(SourceDecoder):

    def __init__(self):
        self.decoder = DecoderType.AWS_KINESIS_DECODER

    @classmethod
    def decode(cls, message: AWSKinesisEventPayload) -> Dict:
        data = base64.b64decode(message.data).decode('utf-8')
        data = json.loads(data)
        return data


class AWSCloudWatchKinesisFirehoseRecordDecoder(SourceDecoder):

    def __init__(self):
        self.decoder = DecoderType.AWS_CLOUDWATCH_KINESIS_DECODER

    @classmethod
    def decode(cls, message: AWSKinesisEventPayload) -> Dict:
        data = gzip.decompress(base64.b64decode(message.data))
        data = json.loads(data)
        return data


class AWSKinesisFirehoseDefaultDecoder(SourceDecoder):

    @classmethod
    def decode(cls, message: AWSKinesisEventPayload) -> List:
        data = base64.b64decode(message.data).decode('utf-8')
        data = json.loads(data)
        return [data]


class AWSCloudWatchKFHDefaultDataDecoder(SourceDecoder):

    @classmethod
    def decode(cls, message: AWSKinesisEventPayload) -> List:
        events = []
        try:
            data = gzip.decompress(base64.b64decode(message.data))
            data = json.loads(data)
            message_type = data.get('messageType', None)
            if message_type and message_type == 'DATA_MESSAGE':
                log_events = data.get('logEvents', None)
                if log_events:
                    for log in log_events:
                        try:
                            log_message = log.get('message', None)
                            if log_message:
                                try:
                                    log_message_json = json.loads(log_message)
                                    events.append(log_message_json)
                                except JSONDecodeError:
                                    events.append(log_message)
                        except Exception as e:
                            logger.error(f'Unable to decode message cloudwatch stream with error: {e}')
                            continue
        except JSONDecodeError:
            logger.error('Unable to decode message cloudwatch stream')
        return events


class DrdCollectorDecoder(SourceDecoder):

    @classmethod
    def decode(cls, message: DrdCollectorEventPayload) -> List:
        data = message.data
        return [data]


class SourceDecoderFacade:

    def __init__(self):
        self._map = {}

    def register(self, decoder_type: DecoderType, decoder: SourceDecoder):
        self._map[decoder_type] = decoder

    def decode(self, decoder_type: DecoderType, message):
        return self._map[decoder_type].decode(message)


decoder_facade = SourceDecoderFacade()
decoder_facade.register(DecoderType.AWS_KINESIS_DECODER, AWSKinesisFirehoseRecordDecoder())
decoder_facade.register(DecoderType.AWS_CLOUDWATCH_KINESIS_DECODER, AWSCloudWatchKinesisFirehoseRecordDecoder())


class DefaultSourceDecoderFacade:

    def __init__(self):
        self._map = {}

    def register(self, source: EventProto.EventSource, decoder: SourceDecoder):
        self._map[source] = decoder

    def decode(self, source: EventProto.EventSource, message):
        if source is None or source not in self._map:
            return DefaultDecoder.decode(message)
        return self._map[source].decode(message)


source_default_decoder_facade = DefaultSourceDecoderFacade()
source_default_decoder_facade.register(EventProto.EventSource.COLLECTOR, DrdCollectorDecoder())
source_default_decoder_facade.register(EventProto.EventSource.SEGMENT, AWSKinesisFirehoseDefaultDecoder())
source_default_decoder_facade.register(EventProto.EventSource.AWS_KINESIS, AWSKinesisFirehoseDefaultDecoder())
source_default_decoder_facade.register(EventProto.EventSource.CLOUDWATCH, AWSCloudWatchKFHDefaultDataDecoder())
