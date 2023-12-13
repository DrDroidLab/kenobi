import time
from datetime import datetime

from urllib.parse import urlsplit

import pytz
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from protos.event.base_pb2 import EventKey as EventKeyProto
from protos.event.schema_pb2 import KeyValue, IngestionEvent, Value as ValueProto


def build_absolute_uri(request, location, protocol=None, enabled=False):
    """request.build_absolute_uri() helper
    like request.build_absolute_uri, but gracefully handling
    the case where request is None.
    """
    if not protocol:
        protocol = settings.SITE_DEFAULT_HTTP_PROTOCOL

    if request is None:
        if not enabled:
            raise ImproperlyConfigured("Passing `request=None` requires `sites` to be enabled")

        site = Site.objects.get_current()
        bits = urlsplit(location)
        if not (bits.scheme and bits.netloc):
            uri = "{protocol}://{domain}{url}".format(
                protocol=protocol,
                domain=site.domain,
                url=location,
            )
        else:
            uri = location
    else:
        uri = request.build_absolute_uri(location)
    # NOTE: We only force a protocol if we are instructed to do so
    # via the `protocol` parameter, or, if the default is set to
    # HTTPS. The latter keeps compatibility with the debatable use
    # case of running your site under both HTTP and HTTPS, where one
    # would want to make sure HTTPS links end up in password reset
    # mails even while they were initiated on an HTTP password reset
    # form.
    # (end NOTE)
    if protocol:
        uri = protocol + ":" + uri.partition(":")[2]
    return uri


def current_milli_time():
    return round(time.time() * 1000)


def current_epoch_timestamp():
    return int(time.time())


def current_datetime(timezone=pytz.utc):
    return datetime.now(timezone)


def infer_value_type(v):
    if isinstance(v, str):
        return EventKeyProto.KeyType.STRING, ValueProto(string_value=v)
    elif isinstance(v, bool):
        return EventKeyProto.KeyType.BOOLEAN, ValueProto(bool_value=v)
    elif isinstance(v, int):
        return EventKeyProto.KeyType.LONG, ValueProto(int_value=v)
    elif isinstance(v, float):
        return EventKeyProto.KeyType.DOUBLE, ValueProto(double_value=v)
    return EventKeyProto.KeyType.UNKNOWN, None


def transform_event_json(event_json: dict):
    if not event_json:
        return None
    event_name: str = event_json.get('name', '')
    if not event_name:
        return None
    payload = event_json.get('payload', None)
    if not isinstance(payload, dict):
        return None

    timestamp_in_ms = event_json.get('timestamp', current_milli_time())

    kvlist = []
    for key, value in payload.items():
        _, proto_value = infer_value_type(value)
        if not proto_value:
            continue
        kvlist.append(KeyValue(key=key, value=proto_value))

    return IngestionEvent(name=event_name, kvs=kvlist, timestamp=timestamp_in_ms)
