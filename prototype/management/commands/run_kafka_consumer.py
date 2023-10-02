import signal
import sys
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from sentry_sdk import capture_exception

from prototype.kafka.consumer import KafkaConsumer


def signal_handler(consumer: KafkaConsumer):
    def fn(signum, frame):
        signame = signal.Signals(signum).name
        print(f'Signal handler called with signal {signame} ({signum})')
        consumer.shutdown()
        return

    return fn


class Command(BaseCommand):
    help = "Process kafka messages from topic"

    def add_arguments(self, parser):
        parser.add_argument(
            "--consumer",
            default=None,
            help=(
                "Consumer to start"
            ),
        )

        parser.add_argument(
            "--group",
            default='console-consumer-group',
            help=(
                "Consumer group for kafka consumer"
            ),
        )

        parser.add_argument(
            "--processor",
            default=None,
            help=(
                "Processor for the kafka consumer"
            ),
        )

        parser.add_argument(
            "--polling-timeout",
            default=0.5,
            type=float,
            help=(
                "Polling timeout for kafka consumer"
            ),
        )

        parser.add_argument(
            "--batch-size",
            default=200,
            type=int,
            help=(
                "Batch size for kafka consumer"
            ),
        )

    def handle(self, *args, **options):
        consumer = options['consumer']
        if not consumer:
            raise CommandError("A consumer needs to be defined which should be present in django settings")
        kafka_consumer_config = getattr(settings, 'KAFKA_CONSUMER_CONFIG', {})
        config = kafka_consumer_config.get(consumer, None)
        if not config:
            raise CommandError("Consumer config is not present in django settings")

        config['config']['group.id'] = options['group']

        processor = config['processor']
        if options.get('processor', None):
            processor = options['processor']
        try:
            consumer = KafkaConsumer(
                # group.instance.id -> This property needs to be added for static member ids
                topic=config['topic'],
                config=config['config'],
                processor_cls=processor,
                batch_size=options['batch_size'],
                polling_timeout=options['polling_timeout']
            )
        except Exception as ex:
            capture_exception(ex)
            print(f"Error initializing KafkaConsumer: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")
            sys.exit(1)

        handler = signal_handler(consumer)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
        while True:
            try:
                consumer.run()
                return
            except Exception as ex:
                capture_exception(ex)
                print(f'Error running consumer: {traceback.format_exception(type(ex), ex, ex.__traceback__)}')
