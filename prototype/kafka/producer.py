from typing import Dict

from confluent_kafka import Producer
from django.conf import settings
from google.protobuf.message import Message


class KafkaProducer:
    def __init__(self, topic: str, config: Dict):
        self._client: Producer = Producer(config)
        self._topic: str = topic

    def shutdown(self):
        self._client.flush()
        return

    def process(self, key: Message, value: Message):
        self._client.produce(topic=self._topic, key=key.SerializeToString(), value=value.SerializeToString())
        return

    def flush(self):
        self._client.flush()
        return


def create_kafka_producers():
    kafka_producer_config = getattr(settings, 'KAFKA_PRODUCER_CONFIG', {})
    producers = {}
    for name, config in kafka_producer_config.items():
        if not config.get('enabled', False):
            continue

        producer = KafkaProducer(topic=config['topic'], config=config['config'])
        producers[name] = producer

    return producers


kafka_producers: Dict = create_kafka_producers()


def get_kafka_producer(name):
    return kafka_producers.get(name, None)
