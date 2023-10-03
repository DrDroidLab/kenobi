import requests

from django.core.mail import send_mail
from django.template.loader import render_to_string

from accounts.models import Account, User
from event.models import Notification, Alert
from event.notification.notification_helper import generate_notification_text
from protos.event.notification_pb2 import NotificationConfig, EmailConfiguration
from protos.event.options_pb2 import NotificationOption


class NotificationFacadeException(ValueError):
    pass


class NotificationFacade:

    @classmethod
    def send_notification(cls, scope, slack_notification_client: Notification, trigger, alert: Alert):
        pass

    @classmethod
    def get_notification_options(cls, scope) -> [NotificationOption]:
        pass


class SlackNotificationFacade(NotificationFacade):

    @classmethod
    def send_notification(cls, scope, slack_notification_client: Notification, trigger, alert: Alert):
        if type(scope) is not Account:
            raise ValueError(f'{scope} needs to be Account')

        headers = {"Content-type": "application/json"}

        data = {
            "text": generate_notification_text(scope, NotificationConfig.Channel.SLACK, alert, trigger)
        }

        requests.post(slack_notification_client.config["webhook_url"], headers=headers, json=data)

    @classmethod
    def get_notification_options(cls, scope) -> [NotificationOption]:
        if type(scope) is not Account:
            raise ValueError(f'{scope} needs to be Account')

        notifications = scope.notification_set.filter(channel=NotificationConfig.Channel.SLACK)

        notification_options: [NotificationOption] = []
        for n in notifications:
            notification_options.append(NotificationOption(channel=n.channel, slack_configuration=n.config))

        return notification_options


class EmailNotificationFacade(NotificationFacade):

    @classmethod
    def send_notification(cls, scope, email_notification_client: Notification, trigger, alert: Alert):
        if type(scope) is not Account:
            raise ValueError(f'{scope} needs to be Account')

        notification_text_config = generate_notification_text(scope, NotificationConfig.Channel.EMAIL, alert, trigger)

        msg_html = render_to_string('alert_email_template.html',
                                    {'trigger_name': notification_text_config["trigger_name"],
                                     'source_name': notification_text_config["source_name"],
                                     'why': notification_text_config["why"],
                                     'when': notification_text_config["when"],
                                     'alert_link': notification_text_config["alert_link"],
                                     'error_type': notification_text_config["error_type"]})
        recipient_email_id = email_notification_client.config["recipient_email_id"]
        send_mail(
            subject=notification_text_config["subject"],
            message=notification_text_config["body"],
            from_email=None,
            recipient_list=[recipient_email_id],
            html_message=msg_html
        )

    @classmethod
    def get_notification_options(cls, scope) -> [NotificationOption]:
        if type(scope) is not User:
            raise ValueError(f'{scope} needs to be User')

        email = scope.email

        notification_options: [NotificationOption] = [NotificationOption(channel=NotificationConfig.Channel.EMAIL,
                                                                         email_configuration=EmailConfiguration(
                                                                             recipient_email_id=email))]

        return notification_options


class NotificationFacadeFactory:
    def __init__(self):
        self._map = {}

    def register(self, channel: NotificationConfig.Channel, notification_facade):
        self._map[channel] = notification_facade

    def notify(self, scope, notifications: [Notification], trigger, alert: Alert):
        for notification in notifications:
            if self._map[notification.channel]:
                self._map[notification.channel].send_notification(scope, notification, trigger, alert)

    def get_notification_options(self, user: User, account: Account) -> [NotificationOption]:
        notification_options: [NotificationOption] = []

        slack_notification_options = self._map[NotificationConfig.Channel.SLACK].get_notification_options(account)
        notification_options.extend(slack_notification_options)

        email_notification_options = self._map[NotificationConfig.Channel.EMAIL].get_notification_options(user)
        notification_options.extend(email_notification_options)
        return notification_options


notification_client = NotificationFacadeFactory()
notification_client.register(NotificationConfig.Channel.SLACK, SlackNotificationFacade())
notification_client.register(NotificationConfig.Channel.EMAIL, EmailNotificationFacade())
