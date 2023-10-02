from django.db.models import Subquery, OuterRef, F, QuerySet, Exists

from event.models import AlertMonitorTransactionMapping
from prototype.aggregates import DistinctFunc
from prototype.utils.timerange import DateTimeRange, filter_dtr


def annotate_entity_stats(account, qs, dtr: DateTimeRange):
    qs = qs.annotate(
        new_instance_count=Subquery(
            filter_dtr(account.entityinstance_set.filter(
                entity=OuterRef('pk'),
                created_at__gt=dtr.time_geq
            ), dtr, 'created_at').annotate(
                count=DistinctFunc(F('id'), function='Count')
            ).values_list('count', flat=True)
        )
    )

    qs = qs.annotate(
        active_instance_count=Subquery(
            filter_dtr(account.entityinstanceeventmapping_set.filter(
                entity=OuterRef('pk'),
            ), dtr, 'event_timestamp').annotate(
                count=DistinctFunc(F('entity_instance'), function='Count')
            ).values_list("count", flat=True)
        )
    )

    qs = qs.annotate(
        event_count=Subquery(
            filter_dtr(account.entityinstanceeventmapping_set.filter(
                entity=OuterRef('pk')
            ), dtr, 'event_timestamp').annotate(
                count=DistinctFunc(F('event'), function='Count')
            ).values_list("count", flat=True)
        )
    )

    qs = qs.annotate(
        transaction_count=Subquery(
            filter_dtr(account.entityinstancemonitortransactionmapping_set.filter(
                entity=OuterRef('pk')
            ), dtr, 'created_at').annotate(
                count=DistinctFunc(F('monitor_transaction'), function='Count')
            ).values_list("count", flat=True)
        )
    )

    return qs


def annotate_entity_instance_stats(account, qs: QuerySet, dtr: DateTimeRange):
    qs = qs.annotate(
        event_count=Subquery(
            filter_dtr(account.entityinstanceeventmapping_set.filter(
                entity_instance=OuterRef('pk'),
            ), dtr, 'created_at').annotate(
                count=DistinctFunc(F('event'), function='Count')
            ).values_list("count", flat=True)
        )
    )
    qs = qs.annotate(
        transaction_count=Subquery(
            filter_dtr(account.entityinstancemonitortransactionmapping_set.filter(
                entity_instance=OuterRef('pk'),
            ), dtr, 'created_at').annotate(
                count=DistinctFunc(F('monitor_transaction'), function='Count')
            ).values_list("count", flat=True)
        )
    )

    qs = qs.annotate(
        has_alerts=Exists(
            account.alertmonitortransactionmapping_set.filter(
                monitor_transaction__entityinstancemonitortransactionmapping__entity_instance=OuterRef('pk'),
            )
        )
    )

    return qs


def annotate_entity_timeline(qs: QuerySet):
    qs = qs.annotate(
        event_type_id=F('event__event_type__id')
    ).annotate(
        event_type_name=F('event__event_type__name')
    ).annotate(
        monitor_transaction_id=F('event__monitortransactioneventmapping__monitor_transaction_id')
    ).annotate(
        transaction=F('event__monitortransactioneventmapping__monitor_transaction__transaction')
    ).annotate(
        monitor_name=F('event__monitortransactioneventmapping__monitor_transaction__monitor__name')
    ).annotate(
        monitor_id=F('event__monitortransactioneventmapping__monitor_transaction__monitor__id')
    ).annotate(
        transaction_event_type=F('event__monitortransactioneventmapping__type')
    ).annotate(
        event_event=F('event__event')
    ).annotate(
        monitor_transaction_has_alert=Exists(
            AlertMonitorTransactionMapping.objects.filter(
                monitor_transaction__in=OuterRef('event__monitortransactioneventmapping__monitor_transaction'),
                account=OuterRef('account'),
                created_at__gte=OuterRef('event_timestamp')
            )
        )
    ).values(
        'id',
        'event_id',
        'event_timestamp',
        'event_event',
        'event_type_id',
        'event_type_name',
        'monitor_transaction_id',
        'transaction',
        'monitor_name',
        'monitor_id',
        'transaction_event_type',
        'monitor_transaction_has_alert'
    )

    return qs
