import base64
import gzip
import json
from typing import Dict

from protos.event.connectors_pb2 import DecoderType
from protos.event.schema_pb2 import AWSKinesisEventPayload


class SourceDecoder:
    decoder_type: DecoderType = None

    @classmethod
    def decode(cls, message):
        pass


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
