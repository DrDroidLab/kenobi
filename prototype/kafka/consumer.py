import time
import traceback
from typing import Dict

from confluent_kafka import Consumer, TIMESTAMP_NOT_AVAILABLE

from prototype.kafka.processor import Processor
from utils.import_utils import import_attribute
from utils.tracer import tracer


def cur_time_milli():
    return int(time.time() * 1000)


def delay_time_milli(prev_time):
    return cur_time_milli() - prev_time


def get_message_process_latency(kafka_timestamp_type, kafka_timestamp):
    if kafka_timestamp_type == TIMESTAMP_NOT_AVAILABLE:
        return None
    return cur_time_milli() - kafka_timestamp


def get_message_delay_time(kafka_timestamp_type, kafka_timestamp, process_time):
    if kafka_timestamp_type == TIMESTAMP_NOT_AVAILABLE:
        return None
    return process_time - kafka_timestamp


def get_message_produce_time(kafka_timestamp_type, kafka_timestamp):
    if kafka_timestamp_type == TIMESTAMP_NOT_AVAILABLE:
        return None
    return kafka_timestamp


class KafkaConsumer:
    def __init__(self, topic: str, config: Dict, processor_cls: str, batch_size: int = 100,
                 polling_timeout: float = 1.0):
        print('Initializing Kafka consumer')
        self._topic = topic
        self._client = Consumer(config)
        self._client.subscribe([topic])
        self._member_id = self._client.memberid()
        self._processor: Processor = import_attribute(processor_cls)()
        self._batch_size = batch_size
        self._polling_timeout = polling_timeout
        self._is_shutting_down = False
        self.log(
            f'Kafka consumer initialized with batch size {self._batch_size} and polling timeout {self._polling_timeout}'
        )
        self._trace_name = f'kafka_consumer.{topic}.consume_msgs'

    def log(self, message):
        if not self._member_id:
            self._member_id = self._client.memberid()
        print(f'Consumer{{{self._member_id}}}: {message}')

    def _consume_msgs(self, msgs):
        with tracer.trace(self._trace_name) as span:
            try:
                keys, values = [], []
                min_msg_produce_time = cur_time_milli()
                for msg in msgs:
                    if msg.error():
                        self.log(f"Consumer error: {msg.error()}")
                        continue
                    key, value = self._processor.transform(key=msg.key(), value=msg.value())
                    keys.append(key)
                    values.append(value)
                    msg_produce_time = get_message_produce_time(*msg.timestamp())
                    if msg_produce_time is not None and msg_produce_time < min_msg_produce_time:
                        min_msg_produce_time = msg_produce_time
                self._processor.process(keys, values)
                num_messages = len(msgs)
                min_msg_delay_time = delay_time_milli(min_msg_produce_time)
                span.set_tag('num_messages', num_messages)
                span.set_tag('min_msg_delay_time', min_msg_delay_time)

                self.log(f'Processed {len(msgs)} message with max delay: {min_msg_delay_time}')
            except Exception as ex:
                span.set_traceback()
                self.log(f'Error processing message: {traceback.format_exception(type(ex), ex, ex.__traceback__)}')

    def run(self):
        self.log(f'Running kafka consumer for {self._topic}')
        while not self._is_shutting_down:
            self.log('Polling on client')
            msgs = self._client.consume(num_messages=self._batch_size, timeout=self._polling_timeout)
            if msgs is None or len(msgs) == 0:
                continue

            self._consume_msgs(msgs)

        if self._is_shutting_down:
            self.log(f'Kafka consumer for {self._topic} is shutting down')
            self._client.close()

    def shutdown(self):
        self._is_shutting_down = True
