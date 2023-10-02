from celery import shared_task

from connectors.models import Connector, ConnectorKey, ConnectorPeriodicRunMetadata
from protos.event.connectors_pb2 import Connector as ConnectorProto, ConnectorKey as ConnectorKeyProto, ConnectorType

from connectors.connector_engine import SentryPollingEngine
    
@shared_task
def sentry_connector_poll_events():
    sentry_connectors = Connector.objects.filter(is_active=True, connector_type=ConnectorType.SENTRY)
    for connector in sentry_connectors:
        sentry_per_connector_poll_events.delay(connector.id)

@shared_task
def sentry_per_connector_poll_events(connector_id):
    connector = Connector.objects.get(id=connector_id)
    polling_engine = SentryPollingEngine(connector)
    polling_engine.poll_sentry_data()


  