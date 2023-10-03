from event.models import Notification
from protos.event.notification_pb2 import NotificationConfig
from utils.proto_utils import proto_to_dict


def create_db_notifications(scope, notifications: [NotificationConfig]):
    db_notifications: [Notification] = []
    for nc in notifications:
        channel_config = None
        which_one_of = nc.WhichOneof('config')
        if nc.channel == NotificationConfig.Channel.SLACK and which_one_of == 'slack_configuration':
            channel_config = proto_to_dict(nc.slack_configuration)
        if nc.channel == NotificationConfig.Channel.EMAIL and which_one_of == 'email_configuration':
            channel_config = proto_to_dict(nc.email_configuration)
        if nc.channel and channel_config:
            db_notifications.append(Notification(config=channel_config, channel=nc.channel))

    saved_notifications = []
    for db_n in db_notifications:
        saved_notification, _ = Notification.objects.get_or_create(account=scope,
                                                                   config=db_n.config,
                                                                   defaults={'channel': db_n.channel})

        saved_notifications.append(saved_notification)
    return saved_notifications
