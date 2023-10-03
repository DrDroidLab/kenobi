import csv
import datetime
import json
import time

import pytz
from celery import shared_task, group
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from django.http import HttpResponse

from accounts.models import Account
from event.cache import GLOBAL_EXPORT_CONTEXT_CACHE
from event.clickhouse.models import Events
from event.engine.query_engine import global_event_search_clickhouse_engine, monitor_transaction_search_engine
from event.models import Alert, MonitorTransactionEventMapping
from event.notification.notification_facade import notification_client
from event.triggers.trigger_processor import process_trigger
from event.triggers.entity_trigger_processor import process_trigger as process_entity_trigger
from management.models import PeriodicTaskStatus
from management.utils.celery_task_signal_utils import publish_pre_run_task, publish_post_run_task, publish_failure_task, \
    get_or_create_task, check_scheduled_or_running_task_run_for_task, \
    create_task_run
from protos.event.api_pb2 import GetEventExportQueryRequest
from protos.event.base_pb2 import Context
from protos.event.entity_pb2 import EntityTriggerDefinition
from protos.event.query_base_pb2 import QueryRequest
from protos.event.trigger_pb2 import TriggerDefinition, DelayedEventTrigger
from protos.event.monitor_pb2 import MonitorTransaction as MonitorTransactionProto
from prototype.db.decorator import use_read_replica
from prototype.utils.timerange import filter_dtr, to_dtr, DateTimeRange
from utils.proto_utils import dict_to_proto, get_value


def get_monitor_transaction_status(status):
    if status == 2:
        return 'Finished'
    return 'Active'


@shared_task
def missing_event_trigger_cron(lookback_interval=None):
    current_time = time.time()
    # publish_pre_run_task(sender='evaluate_missing_event_triggers_for')
    if not lookback_interval or lookback_interval <= 0:
        # adding backlog step to populate alerts for last 3 hours in seconds
        lookback_interval = 10

    tasks = []
    for ac in Account.objects.all():
        # All monitor triggers
        triggers = ac.trigger_set.filter(type=TriggerDefinition.Type.MISSING_EVENT).exclude(is_active=False).exclude(
            monitor__isnull=True).exclude(monitor__is_active=False).values('id', 'type', 'monitor_id', 'config', 'name',
                                                                           'generated_config',
                                                                           'monitor__name',
                                                                           'monitor__primary_key__name',
                                                                           'monitor__secondary_key__event_type__name',
                                                                           'monitor__primary_key__event_type__name')
        for trigger in triggers:
            expected_transaction_time_sec = trigger['config']['transaction_time_threshold']
            time_lower_bound = current_time - expected_transaction_time_sec
            time_upper_bound = time_lower_bound - lookback_interval

            saved_task = get_or_create_task(evaluate_missing_event_triggers_for.__name__, ac.id, trigger,
                                            time_lower_bound, time_upper_bound)

            if check_scheduled_or_running_task_run_for_task(saved_task):
                continue

            task_run = evaluate_missing_event_triggers_for.s(ac.id, trigger, time_lower_bound,
                                                             time_upper_bound)
            task_run_meta = task_run.freeze()

            # Avoid alert noise if expected transaction time is less than a second
            if expected_transaction_time_sec <= 0:
                create_task_run(task=saved_task, task_uuid=task_run_meta.task_id,
                                status=PeriodicTaskStatus.SKIPPED)
                continue

            create_task_run(task=saved_task, task_uuid=task_run_meta.task_id,
                            status=PeriodicTaskStatus.SCHEDULED)

            tasks.append(task_run)

        # All Entity triggers
        triggers = ac.entitytrigger_set.filter(type=EntityTriggerDefinition.TriggerType.PER_EVENT).exclude(
            is_active=False).exclude(
            entity__isnull=True).exclude(entity__is_active=False).values('id', 'type', 'rule_type', 'entity_id', 'config', 'name',
                                                                         'generated_config',
                                                                         'entity__name')

        for trigger in triggers:
            config_time_interval_sec = int(trigger['config'].get('time_interval', 0.0))
            time_lower_bound = current_time - config_time_interval_sec
            time_upper_bound = time_lower_bound - lookback_interval

            saved_task = get_or_create_task(evaluate_entity_event_level_triggers.__name__, ac.id, trigger,
                                            time_lower_bound, time_upper_bound)

            if check_scheduled_or_running_task_run_for_task(saved_task):
                continue

            task_run = evaluate_entity_event_level_triggers.s(ac.id, trigger, time_lower_bound,
                                                              time_upper_bound)
            task_run_meta = task_run.freeze()

            create_task_run(task=saved_task, task_uuid=task_run_meta.task_id,
                            status=PeriodicTaskStatus.SCHEDULED)

            tasks.append(task_run)

    group(tasks).apply_async()


@shared_task(max_retries=3)
def evaluate_entity_event_level_triggers(account_id, trigger, time_lower_bound, time_upper_bound):
    ac: Account = Account.objects.get(id=account_id)
    time_lower_bound_datetime = datetime.datetime.fromtimestamp(time_lower_bound, tz=pytz.utc)
    time_upper_bound_datetime = datetime.datetime.fromtimestamp(time_upper_bound, tz=pytz.utc)
    alerts: [Alert] = process_entity_trigger(ac, trigger, time_lower_bound_datetime, time_upper_bound_datetime)

    notify(ac, trigger, alerts)


@shared_task(max_retries=3)
def evaluate_missing_event_triggers_for(account_id, trigger, time_lower_bound, time_upper_bound):
    ac: Account = Account.objects.get(id=account_id)
    time_lower_bound_datetime = datetime.datetime.fromtimestamp(time_lower_bound, tz=pytz.utc)
    time_upper_bound_datetime = datetime.datetime.fromtimestamp(time_upper_bound, tz=pytz.utc)
    alerts: [Alert] = process_trigger(ac, trigger, time_lower_bound_datetime, time_upper_bound_datetime)

    notify(ac, trigger, alerts)


missing_event_trigger_cron_task_prerun_notifier = publish_pre_run_task(evaluate_missing_event_triggers_for)
missing_event_trigger_cron_task_failure_notifier = publish_failure_task(evaluate_missing_event_triggers_for)
missing_event_trigger_cron_task_postrun_notifier = publish_post_run_task(evaluate_missing_event_triggers_for)


@shared_task
def delayed_event_trigger_cron(lookback_interval=None):
    current_time = time.time()
    if not lookback_interval or lookback_interval <= 0:
        # adding backlog step to populate alerts for last 60 seconds
        lookback_interval = 60

    tasks = []
    for ac in Account.objects.all():
        triggers = ac.trigger_set.filter(type=TriggerDefinition.Type.DELAYED_EVENT).exclude(is_active=False).exclude(
            monitor__isnull=True).exclude(monitor__is_active=False).values('id', 'type', 'monitor_id', 'config',
                                                                           'generated_config',
                                                                           'name',
                                                                           'monitor__name',
                                                                           'monitor__secondary_key__event_type__name',
                                                                           'monitor__primary_key__event_type__name')
        for trigger in triggers:
            trigger_config = dict_to_proto(trigger["config"], DelayedEventTrigger)
            expected_transaction_time_sec = trigger_config.transaction_time_threshold.value
            trigger_resolution = trigger_config.resolution.value
            trigger_threshold = trigger_config.trigger_threshold.value

            time_lower_bound = current_time - expected_transaction_time_sec - lookback_interval
            time_upper_bound = time_lower_bound - trigger_resolution

            saved_task = get_or_create_task(evaluate_delayed_event_triggers_for.__name__, ac.id, trigger,
                                            time_lower_bound, time_upper_bound)

            if check_scheduled_or_running_task_run_for_task(saved_task):
                continue

            task_run = evaluate_delayed_event_triggers_for.s(ac.id, trigger, time_lower_bound, time_upper_bound)
            task_run_meta = task_run.freeze()

            # Avoid alert noise if resolution window is zero or transaction time is less than a second
            if trigger_resolution < settings.DELAYED_EVENT_TRIGGER_RESOLUTION_WINDOW_LOWER_BOUND_IN_SEC or \
                    expected_transaction_time_sec <= 0 or trigger_threshold < 0:
                create_task_run(task=saved_task, task_uuid=task_run_meta.task_id,
                                status=PeriodicTaskStatus.SKIPPED)
                continue

            # Avoid alert noise if alert already generated in the current resolution window
            check_alert_time_lower_bound = datetime.datetime.fromtimestamp(current_time, tz=pytz.utc)
            check_alert_time_upper_bound = datetime.datetime.fromtimestamp(current_time - trigger_resolution,
                                                                           tz=pytz.utc)
            if ac.alert_set.filter(trigger_id=trigger['id']).filter(
                    triggered_at__range=[check_alert_time_upper_bound, check_alert_time_lower_bound]).count() > 0:
                create_task_run(task=saved_task, task_uuid=task_run_meta.task_id,
                                status=PeriodicTaskStatus.SKIPPED)
                continue

            create_task_run(task=saved_task, task_uuid=task_run_meta.task_id,
                            status=PeriodicTaskStatus.SCHEDULED)
            tasks.append(task_run)

    group(tasks).apply_async()


@shared_task(max_retries=3)
def evaluate_delayed_event_triggers_for(account_id, trigger, time_lower_bound, time_upper_bound):
    ac: Account = Account.objects.get(id=account_id)
    time_lower_bound_datetime = datetime.datetime.fromtimestamp(time_lower_bound, tz=pytz.utc)
    time_upper_bound_datetime = datetime.datetime.fromtimestamp(time_upper_bound, tz=pytz.utc)
    alerts: [Alert] = process_trigger(ac, trigger, time_lower_bound_datetime, time_upper_bound_datetime)

    notify(ac, trigger, alerts)


delayed_event_trigger_cron_task_prerun_notifier = publish_pre_run_task(evaluate_delayed_event_triggers_for)
delayed_event_trigger_cron_task_failure_notifier = publish_failure_task(evaluate_delayed_event_triggers_for)
delayed_event_trigger_cron_task_postrun_notifier = publish_post_run_task(evaluate_delayed_event_triggers_for)


def notify(account: Account, trigger, alerts: [Alert]):
    for alert in alerts:
        notifications = []
        if alert.trigger:
            notifications = account.notification_set.filter(trigger=trigger["id"])
        if alert.entity_trigger:
            notifications = account.notification_set.filter(entity_trigger=trigger["id"])
        notification_client.notify(account, notifications, trigger, alert)


@shared_task(max_retries=3)
def export_task(account_id, export_context: Context, user_email, request_message_json):
    if not account_id or not export_context or not user_email or not request_message_json:
        return False, "Invalid request"

    if not GLOBAL_EXPORT_CONTEXT_CACHE.get(account_id, export_context, user_email):
        return False, "Export context not found"

    export_id = GLOBAL_EXPORT_CONTEXT_CACHE.get(account_id, export_context, user_email)
    if not export_id:
        return False, "Export id not found"

    if export_context == Context.EVENT:
        event_export_task.s(account_id, export_id, user_email, request_message_json).apply_async()
    elif export_context == Context.MONITOR_TRANSACTION:
        monitor_transaction_export_task.s(account_id, export_id, user_email, request_message_json).apply_async()

    GLOBAL_EXPORT_CONTEXT_CACHE.delete(account_id, export_context, user_email)
    return True, ""


@shared_task(max_retries=3)
def event_export_task(account_id, export_id, user_email, request_message_json):
    request_message = dict_to_proto(request_message_json, GetEventExportQueryRequest)
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    query_request: QueryRequest = request_message.query_request

    qs = Events.objects.all()
    qs = filter_dtr(qs, dtr, 'timestamp')
    qs = qs.filter(account_id=account_id)
    qs = global_event_search_clickhouse_engine.process_query(qs, query_request)
    qs = global_event_search_clickhouse_engine.process_ordering(qs, query_request)

    event_protos = [e.proto for e in qs]

    csv_data = [['ID', 'Timestamp', 'Event Type', 'Attributes']]
    for event in event_protos:
        attributes = {}
        for kv in event.kvs:
            attributes[kv.key] = get_value(kv.value)
        csv_data.append([event.id, event.timestamp, event.event_type.name, json.dumps(attributes)])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="file.csv"'
    writer = csv.writer(response)

    for row in csv_data:
        writer.writerow(row)

    email = EmailMessage(
        subject="[Doctor Droid] Event Export: {}".format(export_id),
        body="PFA the exported file for export request: {}".format(export_id),
        from_email=None,
        to=[user_email],
    )

    email.attach('drdroid_events_export.csv', response.getvalue(), 'text/csv')
    email.send()


@shared_task(max_retries=3)
def monitor_transaction_export_task(account_id, export_id, user_email, request_message_json):
    request_message = dict_to_proto(request_message_json, GetEventExportQueryRequest)
    dtr: DateTimeRange = to_dtr(request_message.meta.time_range)
    query_request: QueryRequest = request_message.query_request

    account = Account.objects.get(id=account_id)
    qs = account.monitortransaction_set.all()
    qs = filter_dtr(qs, dtr, 'created_at')
    qs = monitor_transaction_search_engine.process_query(qs, query_request)
    qs = qs.annotate(transaction_time=(Cast(F('monitortransactionstats__stats__transaction_time'), FloatField())))

    qs = qs.select_related('monitor')
    mt_protos = [mt.proto_for_export for mt in qs]

    mt_ids = list(x.id for x in mt_protos)
    mt_events_mapping = MonitorTransactionEventMapping.objects.filter(account_id=account.id,
                                                                      monitor_transaction_id__in=mt_ids).values_list(
        'monitor_transaction_id', 'type', 'event_id')

    mt_events_map = {}
    for mapping in mt_events_mapping:
        if mapping[0] not in mt_events_map:
            mt_events_map[mapping[0]] = []
        mt_events_map[mapping[0]].append(mapping)

    events_map = {}
    events = Events.objects.filter(account_id=account.id, id__in=list(x[2] for x in mt_events_mapping)).values_list(
        'id', 'event_type_name', 'timestamp', 'ingested_event', 'processed_kvs')
    for event in events:
        events_map[event[0]] = event

    csv_data = []

    primary_event_keys_seq = []
    secondary_event_keys_seq = []

    finished_txn = qs.filter(type=MonitorTransactionProto.MonitorTransactionStatus.SECONDARY_RECEIVED).first()
    if finished_txn:
        sample_mt_proto = finished_txn.proto_for_export
    else:
        sample_mt_proto = mt_protos[0]

    csv_data_row = ['Transaction Value', 'Monitor Name', 'Status', 'Has Alerts', 'Transaction Time']
    primary_event = list(filter(lambda x: x[1] == 1, mt_events_map[sample_mt_proto.id]))
    if primary_event:
        primary_event = primary_event[0]
        event_object = events_map[primary_event[2]]
        csv_data_row.append('primary_event_type')
        csv_data_row.append('primary_event_timestamp')
        for kv in json.loads(event_object[3])['kvs']:
            csv_data_row.append("primary_" + kv['key'])
            primary_event_keys_seq.append(kv['key'])

    secondary_event = list(filter(lambda x: x[1] == 2, mt_events_map[sample_mt_proto.id]))
    if secondary_event:
        secondary_event = secondary_event[0]
        event_object = events_map[secondary_event[2]]
        csv_data_row.append('secondary_event_type')
        csv_data_row.append('secondary_event_timestamp')
        for kv in json.loads(event_object[3])['kvs']:
            csv_data_row.append("secondary_" + kv['key'])
            secondary_event_keys_seq.append(kv['key'])

    csv_data.append(csv_data_row)

    for mt in mt_protos:
        csv_data_row = [mt.transaction, mt.monitor.name, get_monitor_transaction_status(mt.status), mt.has_alerts.value,
                        mt.transaction_time.value]
        primary_event = list(filter(lambda x: x[1] == 1, mt_events_map[mt.id]))
        if primary_event:
            primary_event = primary_event[0]
            event_object = events_map[primary_event[2]]
            csv_data_row.append(event_object[1])
            csv_data_row.append(event_object[2].strftime('%Y-%m-%d %H:%M:%S'))
            for k in primary_event_keys_seq:
                csv_data_row.append(event_object[4].get(k, None))

        secondary_event = list(filter(lambda x: x[1] == 2, mt_events_map[mt.id]))
        if secondary_event:
            secondary_event = secondary_event[0]
            event_object = events_map[secondary_event[2]]
            csv_data_row.append(event_object[1])
            csv_data_row.append(event_object[2].strftime('%Y-%m-%d %H:%M:%S'))
            for k in secondary_event_keys_seq:
                csv_data_row.append(event_object[4].get(k, None))

        csv_data.append(csv_data_row)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="file.csv"'
    writer = csv.writer(response)

    for row in csv_data:
        writer.writerow(row)

    email = EmailMessage(
        subject="[Doctor Droid] Event Export: {}".format(export_id),
        body="PFA the exported file for export request: {}".format(export_id),
        from_email=None,
        to=[user_email],
    )

    email.attach('drdroid_monitor_transaction_export.csv', response.getvalue(), 'text/csv')
    email.send()
