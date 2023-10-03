import clickhouse_connect
from django.conf import settings

from utils.singleton import singleton_function


@singleton_function
def get_client():
    config = settings.CLICKHOUSE_CLIENT_CONFIG
    return clickhouse_connect.get_client(**config)
