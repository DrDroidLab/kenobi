import time
from typing import Dict

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from accounts.models import Account
from event.models import MonitorTransaction, Alert
from protos.event.entity_pb2 import EntityTriggerDefinition
from protos.event.notification_pb2 import NotificationConfig
from protos.event.trigger_pb2 import TriggerDefinition

from prototype.utils.utils import build_absolute_uri


def generate_alert_hyperlink(alert_id):
    location = settings.ALERT_PAGE_URL.format(str(alert_id))
    protocol = settings.ALERT_SITE_HTTP_PROTOCOL
    enabled = settings.ALERT_USE_SITE
    try:
        uri = build_absolute_uri(None, location, protocol, enabled)
    except ImproperlyConfigured:
        return ""
    return uri


class NotificationHelperException(ValueError):
    pass


def process_alert_time(event_time):
    if int(event_time / 10) <= 0:
        return "few seconds "
    if int(event_time / 60) <= 0:
        return str(int(event_time)) + " seconds "
    event_time = event_time / 60
    if int(event_time / 60) <= 0:
        return str(int(event_time)) + " minutes "
    event_time = event_time / 60
    if int(event_time / 10) <= 0:
        return str(int(event_time)) + " hours "
    event_time = event_time / 24
    return str(int(event_time)) + " days "


def format_duration(seconds):
    if seconds < 0:
        raise ValueError("Input must be a non-negative integer.")

    if seconds == 0:
        return "0 seconds"

    # Calculate the number of hours, minutes, and seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Create a list to store the time components
    components = []

    # Add components with proper pluralization
    if hours > 1:
        components.append(f"{hours} {'hour' if hours == 1 else 'hours'}")
    if minutes > 2:
        components.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")
    if seconds > 0:
        components.append(f"{seconds} {'second' if seconds == 1 else 'seconds'}")

    # Join the components into a human-readable string
    if len(components) == 1:
        return components[0]
    elif len(components) == 2:
        return " and ".join(components)
    else:
        return ""


def format_date_time(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class NotificationHelper:

    @classmethod
    def generate_missing_event_trigger_notification_text(cls, scope, alert: Alert, trigger):
        pass

    @classmethod
    def generate_delayed_event_trigger_notification_text(cls, scope, alert: Alert, trigger):
        pass


class SlackNotificationHelper(NotificationHelper):

    @classmethod
    def generate_missing_event_trigger_notification_text(cls, scope, alert: Alert, trigger) -> str:
        alert_monitor_transactions = scope.alertmonitortransactionmapping_set.filter(
            alert=alert.id).prefetch_related('monitor_transaction')

        base_text = "*" + "Alert" + "*" + ": " + "`" + trigger["name"] + "`" + " triggered"

        description = "*" + "Why" + "*" + ": "
        for amt in alert_monitor_transactions:
            mt: MonitorTransaction = amt.monitor_transaction
            description += "`" + trigger[
                "monitor__secondary_key__event_type__name"] + "`" + " not received for monitor " + "`" + trigger[
                               "monitor__name"] + "`" + " with in " + "`" + str(
                trigger["config"].get("transaction_time_threshold")) + "`" + " seconds, of " + "`" + trigger[
                               "monitor__primary_key__event_type__name"] + "`" + " for " + "`" + trigger[
                               "monitor__primary_key__name"] + "`" + " = > " + "`" + str(mt.transaction) + "`"

        diff = int(time.time()) - int(alert.triggered_at.timestamp())
        time_diff = process_alert_time(diff)
        time_stamp = "*" + "When" + "*" + ": " + "`" + time_diff + "ago" + "`" + " (" + str(
            format_date_time(alert.triggered_at.replace(microsecond=0))) + ")"

        alert_link = "*" + "See More Details: " + "*" + ": " + generate_alert_hyperlink(alert.id)

        return base_text + "\n" + description + "\n" + time_stamp + "\n" + alert_link

    @classmethod
    def generate_per_event_entity_trigger_notification_text(cls, scope, alert: Alert, trigger) -> str:
        base_text = "*" + "Alert" + "*" + ": " + "`" + trigger["name"] + "`" + " triggered"
        description = "*" + "Why" + "*" + ": "

        entity_instance_value = alert.stats['entity_instance_value']
        event_key_name = alert.stats['event_key_name']
        event_timestamp = alert.stats['event_timestamp']
        event_name = alert.stats['event_name']
        entity_name = trigger['entity__name']

        if trigger['rule_type'] == EntityTriggerDefinition.EntityTriggerRuleType.LAST_EVENT:
            time_gap = format_duration(int(trigger['config'].get('time_interval', 0)))
            description += (
                    "No event was received for `" + time_gap + "`" + " after event `" + event_name + "` occurred at `" + str(
                format_date_time(alert.triggered_at.replace(
                    microsecond=0))) + " UTC" + "` for entity `" + entity_name + "`" + " with " + "`" + event_key_name + "`" + " -> " + "`" + entity_instance_value + "`")

        if trigger['rule_type'] == EntityTriggerDefinition.EntityTriggerRuleType.EVENT_COUNT:
            time_gap = format_duration(int(trigger['config'].get('time_interval', 0)))
            threshold_count = int(trigger['config'].get('threshold_count', 0))
            if threshold_count == 1:
                threshold_count_str = "once"
            else:
                threshold_count_str = str(threshold_count) + " times"
            description += (
                    "Event `" + event_name + "` was received more than `" + threshold_count_str + "` within `" + time_gap + "` for entity `" + entity_name + "`" + " with " + "`" + event_key_name + "`" + " -> " + "`" + entity_instance_value + "`")

        if trigger['rule_type'] == EntityTriggerDefinition.EntityTriggerRuleType.EVENT_OCCURS:
            description += (
                    "Event `" + event_name + "` was received for entity `" + entity_name + "`" + " with " + "`" + event_key_name + "`" + " -> " + "`" + entity_instance_value + "`")

        diff = int(time.time()) - int(alert.triggered_at.timestamp())
        time_diff = process_alert_time(diff)
        time_stamp = "*" + "When" + "*" + ": " + "`" + time_diff + "ago" + "`" + " (" + str(
            format_date_time(alert.triggered_at.replace(microsecond=0))) + " UTC)"

        alert_link = "*" + "See More Details: " + "*" + ": " + generate_alert_hyperlink(alert.id)

        return base_text + "\n" + description + "\n" + time_stamp + "\n" + alert_link

    @classmethod
    def generate_delayed_event_trigger_notification_text(cls, scope, alert: Alert, trigger) -> str:
        base_text = "*" + "Alert" + "*" + ": " + "`" + trigger["name"] + "`" + " triggered"

        resolution_time = process_alert_time(trigger["config"].get("resolution"))
        description = "*" + "Why" + "*" + ": " + str(
            trigger["config"].get("trigger_threshold")) + " % transactions did not receive " + "`" + trigger[
                          "monitor__secondary_key__event_type__name"] + "`" + " from " + "`" + trigger[
                          "monitor__primary_key__event_type__name"] + "`" + " within " + str(trigger["config"].get(
            "transaction_time_threshold")) + " seconds" + " for monitor: " + "`" + trigger[
                          "monitor__name"] + "`" + " in last " + "`" + resolution_time + "`"

        diff = int(time.time()) - int(alert.triggered_at.timestamp())
        time_diff = process_alert_time(diff)
        time_stamp = "*" + "When" + "*" + ": " + "`" + time_diff + "ago" + "`" + " (" + str(
            format_date_time(alert.triggered_at.replace(microsecond=0))) + ")"

        alert_link = "*" + "See More Details: " + "*" + ": " + generate_alert_hyperlink(alert.id)

        return base_text + "\n" + description + "\n" + time_stamp + "\n" + alert_link


class EmailNotificationHelper(NotificationHelper):

    @classmethod
    def generate_missing_event_trigger_notification_text(cls, scope, alert: Alert, trigger) -> Dict:
        alert_monitor_transactions = scope.alertmonitortransactionmapping_set.filter(
            alert=alert.id).prefetch_related('monitor_transaction')

        trigger_name = trigger["name"]
        monitor_name = trigger["monitor__name"]

        description = ""
        for amt in alert_monitor_transactions:
            mt: MonitorTransaction = amt.monitor_transaction
            description += trigger[
                               "monitor__secondary_key__event_type__name"] + " not received for " + trigger[
                               "monitor__primary_key__event_type__name"] + " within " + str(
                trigger["config"].get("transaction_time_threshold")) + " seconds from " + trigger[
                               "monitor__primary_key__name"] + " => " + str(mt.transaction)

        time_stamp = str(format_date_time(alert.triggered_at.replace(microsecond=0)))

        alert_link = generate_alert_hyperlink(alert.id)

        body = description + "\n" + time_stamp + "\n" + alert_link

        subject = "Alert: " + monitor_name + " -> " + "Missing Event Alert"

        return {"trigger_name": trigger_name, "source_name": monitor_name, "subject": subject, "body": body,
                "why": description, "when": time_stamp, "alert_link": alert_link, "error_type": "Missing Event Alert"}

    @classmethod
    def generate_per_event_entity_trigger_notification_text(cls, scope, alert: Alert, trigger) -> Dict:
        description = ""

        entity_instance_value = alert.stats['entity_instance_value']
        event_key_name = alert.stats['event_key_name']
        event_name = alert.stats['event_name']
        entity_name = trigger['entity__name']
        trigger_name = alert.entity_trigger.name

        if trigger['rule_type'] == EntityTriggerDefinition.EntityTriggerRuleType.LAST_EVENT:
            time_gap = format_duration(int(trigger['config'].get('time_interval', 0)))
            description += (
                    "No event was received for " + time_gap + " after event " + event_name + " occurred at " + str(
                format_date_time(alert.triggered_at.replace(
                    microsecond=0))) + " UTC" + " for entity " + entity_name + " with " + event_key_name + " -> " + entity_instance_value)

        if trigger['rule_type'] == EntityTriggerDefinition.EntityTriggerRuleType.EVENT_COUNT:
            time_gap = format_duration(int(trigger['config'].get('time_interval', 0)))
            threshold_count = int(trigger['config'].get('threshold_count', 0))
            if threshold_count == 1:
                threshold_count_str = "once"
            else:
                threshold_count_str = str(threshold_count) + " times"
            description += (
                    "Event " + event_name + " was received more than " + threshold_count_str + " within " + time_gap + " for entity " + entity_nam + " with " + event_key_name + " -> " + entity_instance_value)

        if trigger['rule_type'] == EntityTriggerDefinition.EntityTriggerRuleType.EVENT_OCCURS:
            description += (
                    "Event " + event_name + " was received for entity " + entity_name + " with " + event_key_name + " -> " + entity_instance_value)

        time_stamp = str(format_date_time(alert.triggered_at.replace(microsecond=0)))
        alert_link = generate_alert_hyperlink(alert.id)

        subject = "Alert: " + entity_name + " -> " + "Events Alert"
        body = description + "\n" + time_stamp + "\n" + alert_link

        return {"trigger_name": trigger_name, "source_name": entity_name, "subject": subject, "body": body,
                "why": description, "when": time_stamp, "alert_link": alert_link, "error_type": "Event Alert"}

    @classmethod
    def generate_delayed_event_trigger_notification_text(cls, scope, alert: Alert, trigger) -> Dict:
        trigger_name = trigger["name"]
        monitor_name = trigger["monitor__name"]

        resolution_time = process_alert_time(trigger["config"].get("resolution"))
        description = str(
            trigger["config"].get("trigger_threshold")) + " % transactions did not receive " + trigger[
                          "monitor__secondary_key__event_type__name"] + " after " + trigger[
                          "monitor__primary_key__event_type__name"] + " within " + str(trigger["config"].get(
            "transaction_time_threshold")) + " seconds" + " in last " + resolution_time

        time_stamp = str(format_date_time(alert.triggered_at.replace(microsecond=0)))

        alert_link = generate_alert_hyperlink(alert.id)

        body = description + "\n" + time_stamp + "\n" + alert_link

        subject = "Alert: " + monitor_name + " -> " + "Aggregated Events Alert"

        return {"trigger_name": trigger_name, "source_name": monitor_name, "subject": subject, "body": body,
                "why": description, "when": time_stamp, "alert_link": alert_link,
                "error_type": "Aggregated Events Alert"}


class NotificationHelperFactory:

    def __init__(self):
        self._map = {}

    def register(self, channel_type: NotificationConfig.Channel, notification_helper: NotificationHelper):
        self._map[channel_type] = notification_helper

    def generate_missing_event_trigger_text(self, scope, channel_type: NotificationConfig.Channel, alert: Alert,
                                            trigger) -> str:
        return self._map[channel_type].generate_missing_event_trigger_notification_text(scope, alert, trigger)

    def generate_per_event_entity_trigger_text(self, scope, channel_type: NotificationConfig.Channel, alert: Alert,
                                               trigger) -> str:
        return self._map[channel_type].generate_per_event_entity_trigger_notification_text(scope, alert, trigger)

    def generate_delayed_event_trigger_text(self, scope, channel_type: NotificationConfig.Channel, alert: Alert,
                                            trigger) -> str:
        return self._map[channel_type].generate_delayed_event_trigger_notification_text(scope, alert, trigger)


notification_helper_factory = NotificationHelperFactory()
notification_helper_factory.register(TriggerDefinition.Type.MISSING_EVENT, SlackNotificationHelper())
notification_helper_factory.register(TriggerDefinition.Type.DELAYED_EVENT, EmailNotificationHelper())


def generate_notification_text(scope, channel_type: NotificationConfig.Channel, alert: Alert, trigger) -> str:
    if type(scope) is not Account:
        raise ValueError(f'{scope} needs to be Account')

    if alert.trigger:
        if trigger["type"] == TriggerDefinition.MISSING_EVENT:
            return notification_helper_factory.generate_missing_event_trigger_text(scope, channel_type, alert, trigger)
        elif trigger["type"] == TriggerDefinition.DELAYED_EVENT:
            return notification_helper_factory.generate_delayed_event_trigger_text(scope, channel_type, alert, trigger)

    if alert.entity_trigger:
        if trigger["type"] == EntityTriggerDefinition.TriggerType.PER_EVENT:
            return notification_helper_factory.generate_per_event_entity_trigger_text(scope, channel_type, alert,
                                                                                      trigger)
