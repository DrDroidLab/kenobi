import traceback

from django.conf import settings
from django.core.cache import caches
from sentry_sdk import capture_exception

from protos.event.base_pb2 import Context


class PanelCache:
    def __init__(self, cache_key, enabled):
        self._cache_key = cache_key
        self._enabled = enabled

    def get(self, account_id, name=None):
        try:
            if name:
                key = f'panel:{account_id}:{name}'
                value = caches[self._cache_key].get(key)
                return [value]
            c = caches[self._cache_key]
            values = [c.get(k) for k in c.keys(f'panel:{account_id}:*')]
            return values
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while getting panel config from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    def create_or_update(self, account_id, name, panel, time_to_expire_s=None):
        try:
            key = f'panel:{account_id}:{name}'
            caches[self._cache_key].set(key, panel, timeout=time_to_expire_s)
            if not time_to_expire_s:
                caches[self._cache_key].persist(key)
            return panel, True
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while setting panel config from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    def delete(self, account_id, name):
        try:
            if name:
                key = f'panel:{account_id}:{name}'
                value = caches[self._cache_key].delete(key)
                return [value]
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while deleting panel config from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")


class DashboardCache:
    def __init__(self, cache_key, enabled):
        self._cache_key = cache_key
        self._enabled = enabled

    def get(self, account_id, name=None):
        try:
            if name:
                key = f'dashboard:{account_id}:{name}'
                value = caches[self._cache_key].get(key)
                return [value]
            c = caches[self._cache_key]
            values = [c.get(k) for k in c.keys(f'dashboard:{account_id}:*')]
            return values
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while getting/setting dashboard config from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    def create_or_update(self, account_id, name, dashboard, time_to_expire_s=None):
        try:
            key = f'dashboard:{account_id}:{name}'
            caches[self._cache_key].set(key, dashboard, time_to_expire_s)
            if not time_to_expire_s:
                caches[self._cache_key].persist(key, dashboard, time_to_expire_s)
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while setting dashboard config in cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    def delete(self, account_id, name):
        try:
            if name:
                key = f'dashboard:{account_id}:{name}'
                value = caches[self._cache_key].delete(key)
                return [value]
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while deleting dashboard config from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")


class EventSearchQueryRequestCache:
    def __init__(self, cache_key, enabled):
        self._cache_key = cache_key
        self._enabled = enabled

    def get(self, account_id, search_context_id=None):
        try:
            if not search_context_id:
                raise Exception("search_context_id is required")

            key = f'event_search_query:{account_id}:{search_context_id}'
            return caches[self._cache_key].get(key)
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while getting event search query from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    def create_or_update(self, account_id, search_context_id, event_search_query_request, time_to_expire_s=None):
        try:
            if not time_to_expire_s:
                time_to_expire_s = 60 * 60 * 24 * 2
            key = f'event_search_query:{account_id}:{search_context_id}'
            caches[self._cache_key].set(key, event_search_query_request, time_to_expire_s)
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while setting event search query in cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    def delete(self, account_id, search_context_id):
        try:
            if not search_context_id:
                raise Exception("search_context_id is required")

            key = f'event_search_query:{account_id}:{search_context_id}'
            value = caches[self._cache_key].delete(key)
            return value
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while deleting event search querty  from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")


class MonitorTransactionSearchQueryRequestCache:
    def __init__(self, cache_key, enabled):
        self._cache_key = cache_key
        self._enabled = enabled

    def get(self, account_id, search_context_id=None):
        try:
            if not search_context_id:
                raise Exception("search_context_id is required")

            key = f'monitor_transaction_search_query:{account_id}:{search_context_id}'
            return caches[self._cache_key].get(key)
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while getting monitor transaction search query from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    def create_or_update(self, account_id, search_context_id, event_search_query_request, time_to_expire_s=None):
        try:
            if not time_to_expire_s:
                time_to_expire_s = 60 * 60 * 24 * 2
            key = f'monitor_transaction_search_query:{account_id}:{search_context_id}'
            caches[self._cache_key].set(key, event_search_query_request, time_to_expire_s)
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while setting monitor transaction search query in cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    def delete(self, account_id, search_context_id):
        try:
            if not search_context_id:
                raise Exception("search_context_id is required")

            key = f'monitor_transaction_search_query:{account_id}:{search_context_id}'
            value = caches[self._cache_key].delete(key)
            return value
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while deleting monitor transaction search query from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")


class ExportRequestCache:
    def __init__(self, cache_key, enabled):
        self._cache_key = cache_key
        self._enabled = enabled

    def get(self, account_id, export_context: Context, user_email):
        try:
            if not account_id or not export_context or not user_email:
                raise Exception("Missing required fields [account_id, export_context, user_email]")

            key = f'export_request:{account_id}:{export_context}:{user_email}:'
            return caches[self._cache_key].get(key)
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while getting export context from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    def create_or_update(self, account_id, export_context: Context, user_email, export_id, time_to_expire_s=None):
        try:
            if not account_id or not export_context or not user_email:
                raise Exception("Missing required fields [account_id, export_context, user_email]")
            if not time_to_expire_s:
                time_to_expire_s = 60 * 60
            key = f'export_request:{account_id}:{export_context}:{user_email}:'
            caches[self._cache_key].set(key, export_id, time_to_expire_s)
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while setting export context in cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")

    def delete(self, account_id, export_context: Context, user_email):
        try:
            if not account_id or not export_context or not user_email:
                raise Exception("Missing required fields [account_id, export_context, user_email]")
            key = f'export_request:{account_id}:{export_context}:{user_email}:'
            value = caches[self._cache_key].delete(key)
            return value
        except Exception as ex:
            capture_exception(ex)
            print(
                f"Error while deleting monitor transaction search query from cache:: {traceback.format_exception(type(ex), ex, ex.__traceback__)}")


GLOBAL_PANEL_CACHE = PanelCache(**settings.GLOBAL_PANEL_CACHE)
GLOBAL_DASHBOARD_CACHE = DashboardCache(**settings.GLOBAL_DASHBOARD_CACHE)
GLOBAL_EVENT_QUERY_SEARCH_REQUEST_CACHE = EventSearchQueryRequestCache(
    **settings.GLOBAL_EVENT_QUERY_SEARCH_REQUEST_CACHE)
GLOBAL_MONITOR_TRANSACTION_QUERY_SEARCH_REQUEST_CACHE = MonitorTransactionSearchQueryRequestCache(
    **settings.GLOBAL_MONITOR_TRANSACTION_QUERY_SEARCH_REQUEST_CACHE)
GLOBAL_EXPORT_CONTEXT_CACHE = ExportRequestCache(**settings.GLOBAL_EXPORT_CONTEXT_CACHE)
