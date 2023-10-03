from django.conf import settings
from django.core.cache import caches

from event.models import EventType, EventKey


class EventTypeCache:
    def __init__(self, cache_key, enabled):
        self._cache_key = cache_key
        self._enabled = enabled

    def _get_or_create(self, **kwargs):
        return EventType.objects.get_or_create(**kwargs)

    def get_or_create(self, account_id, name):
        if not self._enabled:
            return self._get_or_create(account_id=account_id, name=name)

        key = f'event_type:{account_id}:{name}'
        value = caches[self._cache_key].get(key)
        if value is not None:
            return value, False
        obj, created = self._get_or_create(account_id=account_id, name=name)
        caches[self._cache_key].set(key, obj)
        return obj, created

    def update(self, obj, update_fields=None):
        if not self._enabled:
            obj.save(update_fields=update_fields)

        obj.save(update_fields=update_fields)
        key = f'event_type:{obj.account_id}:{obj.name}'
        caches[self._cache_key].set(key, obj)


class EventKeyCache:
    def __init__(self, cache_key, enabled):
        self._cache_key = cache_key
        self._enabled = enabled

    def _get_or_create(self, **kwargs):
        return EventKey.objects.get_or_create(**kwargs)

    def get_or_create(self, account_id, event_type_id, name, defaults=None):
        if not self._enabled:
            return self._get_or_create(
                account_id=account_id, event_type_id=event_type_id, name=name,
                defaults=defaults
            )

        key = f'event_key:{account_id}:{event_type_id}:{name}'
        value = caches[self._cache_key].get(key)
        if value is not None:
            return value, False
        obj, created = self._get_or_create(
            account_id=account_id, event_type_id=event_type_id, name=name,
            defaults=defaults
        )
        caches[self._cache_key].set(key, obj)
        return obj, created


GLOBAL_EVENT_TYPE_CACHE = EventTypeCache(**settings.GLOBAL_EVENT_TYPE_CACHE)
GLOBAL_EVENT_KEY_CACHE = EventKeyCache(**settings.GLOBAL_EVENT_KEY_CACHE)
