from datetime import datetime, timedelta

from accounts.models import Account
from event.processors.process_events_payload import process_account_events_payload
from protos.event.base_pb2 import Event as EventProto
from protos.event.schema_pb2 import IngestionEventPayload, IngestionEvent, KeyValue, Value


def get_sample_event_payload():
    current_time = datetime.utcnow()
    lookback_120s = int((current_time - timedelta(seconds=120)).timestamp() * 1000)
    lookback_115s = int((current_time - timedelta(seconds=115)).timestamp() * 1000)
    lookback_112s = int((current_time - timedelta(seconds=112)).timestamp() * 1000)
    lookback_60s = int((current_time - timedelta(seconds=60)).timestamp() * 1000)
    lookback_55s = int((current_time - timedelta(seconds=55)).timestamp() * 1000)
    lookback_now = int(current_time.timestamp() * 1000)
    return IngestionEventPayload(
        events=[
            IngestionEvent(
                name="payment_started",
                kvs=[
                    KeyValue(
                        key="transaction_id",
                        value=Value(string_value="si_LULhDM2vvvt7yZ")
                    ),
                    KeyValue(
                        key="amount",
                        value=Value(double_value=54.8)
                    ),
                    KeyValue(
                        key="currency",
                        value=Value(string_value="usd")
                    ),
                    KeyValue(
                        key="invoice_id",
                        value=Value(string_value="in_1KnN0G589O8KAxCGfVSpD0Pj")
                    )
                ],
                timestamp=lookback_120s
            ),
            IngestionEvent(
                name="payment_started",
                kvs=[
                    KeyValue(
                        key="transaction_id",
                        value=Value(string_value="si_ekpsHJ9GhQd7OU")
                    ),
                    KeyValue(
                        key="amount",
                        value=Value(double_value=12.4)
                    ),
                    KeyValue(
                        key="currency",
                        value=Value(string_value="usd")
                    ),
                    KeyValue(
                        key="invoice_id",
                        value=Value(string_value="in_98363ixIwXnh07L5DuLvQE6c")
                    )
                ],
                timestamp=lookback_115s
            ),
            IngestionEvent(
                name="payment_started",
                kvs=[
                    KeyValue(
                        key="transaction_id",
                        value=Value(string_value="si_4i7w711u93uH46")
                    ),
                    KeyValue(
                        key="amount",
                        value=Value(double_value=8.7)
                    ),
                    KeyValue(
                        key="currency",
                        value=Value(string_value="usd")
                    ),
                    KeyValue(
                        key="invoice_id",
                        value=Value(string_value="in_QezX99uPQSrgbgpP82U6YUu6")
                    )
                ],
                timestamp=lookback_112s
            ),
            IngestionEvent(
                name="payment_started",
                kvs=[
                    KeyValue(
                        key="transaction_id",
                        value=Value(string_value="si_2v0fm8274y9nem")
                    ),
                    KeyValue(
                        key="amount",
                        value=Value(double_value=23.9)
                    ),
                    KeyValue(
                        key="currency",
                        value=Value(string_value="usd")
                    ),
                    KeyValue(
                        key="invoice_id",
                        value=Value(string_value="in_B31kppK5qEF7Dv5S13D0VZ6B")
                    )
                ],
                timestamp=lookback_60s
            ),
            IngestionEvent(
                name="payment_started",
                kvs=[
                    KeyValue(
                        key="transaction_id",
                        value=Value(string_value="si_tWaIb3aK3vlHn9")
                    ),
                    KeyValue(
                        key="amount",
                        value=Value(double_value=6.8)
                    ),
                    KeyValue(
                        key="currency",
                        value=Value(string_value="usd")
                    ),
                    KeyValue(
                        key="invoice_id",
                        value=Value(string_value="in_U0T8TO2dDAKxxtzO4cG3Dr3l")
                    )
                ],
                timestamp=lookback_55s
            ),
            IngestionEvent(
                name="payment_callback",
                kvs=[
                    KeyValue(
                        key="transaction_id",
                        value=Value(string_value="si_LULhDM2vvvt7yZ")
                    ),
                    KeyValue(
                        key="status",
                        value=Value(string_value="paid")
                    ),
                    KeyValue(
                        key="payment_method",
                        value=Value(string_value="cc")
                    )
                ],
                timestamp=lookback_60s
            ),
            IngestionEvent(
                name="payment_callback",
                kvs=[
                    KeyValue(
                        key="transaction_id",
                        value=Value(string_value="si_ekpsHJ9GhQd7OU")
                    ),
                    KeyValue(
                        key="status",
                        value=Value(string_value="paid")
                    ),
                    KeyValue(
                        key="payment_method",
                        value=Value(string_value="venmo")
                    )
                ],
                timestamp=lookback_55s
            ),
            IngestionEvent(
                name="payment_callback",
                kvs=[
                    KeyValue(
                        key="transaction_id",
                        value=Value(string_value="si_4i7w711u93uH46")
                    ),
                    KeyValue(
                        key="status",
                        value=Value(string_value="paid")
                    ),
                    KeyValue(
                        key="payment_method",
                        value=Value(string_value="cc")
                    )
                ],
                timestamp=lookback_now
            ),
            IngestionEvent(
                name="payment_callback",
                kvs=[
                    KeyValue(
                        key="transaction_id",
                        value=Value(string_value="si_2v0fm8274y9nem")
                    ),
                    KeyValue(
                        key="status",
                        value=Value(string_value="failed")
                    ),
                ],
                timestamp=lookback_now
            )
        ]
    )


def setup_account_event_data(account: Account):
    process_account_events_payload(account=account, payload=get_sample_event_payload(),
                                   source=EventProto.EventSource.SAMPLE, is_generated=True,
                                   evaluate_event_monitors=False)

    return
