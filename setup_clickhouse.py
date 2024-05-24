import clickhouse_connect
import os

host = os.getenv("CLICKHOUSE_HOST")
username = os.getenv("CLICKHOUSE_USERNAME")
password = os.getenv("CLICKHOUSE_PASSWORD")
port = os.getenv("CLICKHOUSE_PORT")

client = clickhouse_connect.get_client(host=host, username=username, password=password, port=port)

client.command('CREATE DATABASE IF NOT EXISTS default;')
client.command('USE default;')
client.command('SET allow_experimental_object_type=1;')
client.command(
'''
SET allow_experimental_object_type=1;
CREATE TABLE IF NOT EXISTS events (
    id UInt64,
    account_id UInt64,
    created_at DateTime64(3, 'UTC') default now(),
    timestamp DateTime64(3, 'UTC') default now(),
    event_type_id UInt64,
    event_type_name VARCHAR(256),
    event_source UInt16,
    processed_kvs JSON,
    ingested_event  String
)
ENGINE = MergeTree()
PARTITION BY toDate(timestamp)
ORDER BY (account_id, event_type_id, timestamp)
PRIMARY KEY (account_id, event_type_id, timestamp)
TTL toDateTime(created_at) + INTERVAL 30 DAY DELETE;
'''
)