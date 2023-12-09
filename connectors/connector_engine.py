import requests
import datetime
import math

from connectors.models import ConnectorKey
from event.processors.process_events_payload import process_account_events_payload
from protos.event.connectors_pb2 import ConnectorKey as ConnectorKeyProto

from protos.event.schema_pb2 import IngestionEventPayload
from event.views import transform_event_json


def event_qualifies(timestamp, time_range):
    timestamp_time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").timestamp()
    start_time = datetime.datetime.strptime(time_range[0], "%Y-%m-%dT%H:%M:%S").timestamp()
    end_time = datetime.datetime.strptime(time_range[1], "%Y-%m-%dT%H:%M:%S").timestamp()

    if start_time <= timestamp_time < end_time:
        return True
    return False


def matches_user(ev, user_id, user_ip):
    if (user_id and ev.get('user', {}).get('id') == user_id) or (
            user_ip and ev.get('user', {}).get('ip_address') == user_ip):
        return True
    return False


class SentryPollingEngine():
    SENTRY_EVENT_TYPE_MAP = {'error': 'Sentry_Error', 'warning': 'Sentry_Warning'}
    TAGS_BLACKLIST = ['environment', 'handled', 'level', 'logger', 'mechanism', 'runtime', 'runtime.name']
    SENTRY_PROJECT_URL = 'https://sentry.io/api/0/projects/'
    SENTRY_EVENTS_URL = 'https://sentry.io/api/0/issues/{}/events/'

    def __init__(self, connector, chunk_offset=2):
        self.connector = connector

        try:
            sentry_key = ConnectorKey.objects.get(connector=self.connector,
                                                  key_type=ConnectorKeyProto.KeyType.SENTRY_API_KEY,
                                                  is_active=True).key

            self.SENTRY_BEARER_TOKEN = sentry_key
            self.HEADERS = {
                'Authorization': 'Bearer {}'.format(self.SENTRY_BEARER_TOKEN)
            }
            self.CHUNK_SIZE = int(self.connector.metadata.get('polling_frequency', 300))
            self.CHUNK_OFFSET = chunk_offset
            self.HOURS_OFFSET = math.ceil((self.CHUNK_OFFSET * self.CHUNK_SIZE) / 3600) + 1

            self.projects = self.get_sentry_projects()
        except ConnectorKey.DoesNotExist:
            raise Exception("Sentry API key not found for connector {}".format(self.connector.name))

    def get_sentry_projects(self):
        url = self.SENTRY_PROJECT_URL
        response = requests.request("GET", url, headers=self.HEADERS)

        projects = response.json()
        slugs = list((x['organization']['slug'], x['slug']) for x in projects)

        return slugs

    def get_issue_level_events(self, issue_id, time_range):

        events = []
        url = self.SENTRY_EVENTS_URL.format(issue_id)
        response = requests.request("GET", url, headers=self.HEADERS)
        event_data = response.json()

        for ev in event_data:
            if event_qualifies(ev['dateCreated'], time_range):
                events.append(ev)
        return events

    def get_error_events(self, error, sentry_data, time_range):
        result = {}
        id = error['id']
        events = self.get_issue_level_events(id, time_range)
        sentry_data += events

    def get_user_level_sentry_errors(self, project_slug, start_time_str, end_time_str):

        sentry_data = []

        url = self.SENTRY_PROJECT_URL + project_slug[0] + "/" + project_slug[
            1] + "/issues/?query={}".format("timestamp:>{} timestamp:<{}".format(start_time_str, end_time_str))
        response = requests.request("GET", url, headers=self.HEADERS)
        error_data = response.json()

        for e in error_data:
            self.get_error_events(e, sentry_data, (start_time_str, end_time_str))
        return sentry_data

    def create_error_timeline(self, sentry_errors, user_id, user_ip):
        result = []

        for se in sentry_errors:
            message = ""
            t_obj = {'transaction': list(filter(lambda x: x['key'] == 'transaction', se['tags']))[0]['value'],
                     'title': se['title'], 'type': se['event.type'], 'message': se['message'],
                     'timestamp': se['dateCreated'], 'epoch_timestamp': datetime.datetime.strptime(se['dateCreated'],
                                                                                                   "%Y-%m-%dT%H:%M:%SZ").timestamp()}

            if user_ip:
                message = "Received {} => [{}] in transaction {} from the user's IP address at {}".format(
                    t_obj['type'], t_obj['title'], t_obj['transaction'], t_obj['timestamp'])

            if user_id:
                message = "Received {} => [{}] in transaction {} for the user at {}".format(t_obj['type'],
                                                                                            t_obj['title'],
                                                                                            t_obj['transaction'],
                                                                                            t_obj['timestamp'])

            result.append({'message': message, 't_obj': t_obj})

        return result

    def get_polling_period_time_range(self, current_time):
        start_offset_time = (current_time - datetime.timedelta(hours=self.HOURS_OFFSET)).replace(minute=0, second=0)
        current_date_chunks = []

        end_time = start_offset_time

        while end_time <= current_time:
            period_start_time = end_time
            end_time = period_start_time + datetime.timedelta(seconds=self.CHUNK_SIZE)
            current_date_chunks.append((period_start_time, end_time))

        return current_date_chunks[-self.CHUNK_OFFSET]

    def create_events(self, errors_data):
        events = []

        if errors_data:
            for err in errors_data:
                ev_name = self.SENTRY_EVENT_TYPE_MAP.get(err['event.type'], 'Sentry_Error')
                ev_timestamp = datetime.datetime.strptime(err['dateCreated'],
                                                          "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000
                ev = {'message': err['message'], 'title': err['title']}

                if err.get('user'):
                    if err.get('user').get('id'):
                        ev['user_id'] = err.get('user').get('id')
                    if err.get('user').get('ip'):
                        ev['user_ip'] = err.get('user').get('ip')
                    if err.get('user').get('email'):
                        ev['user_email'] = err.get('user').get('email')

                for tag in err['tags']:
                    if tag['key'] not in self.TAGS_BLACKLIST:
                        ev[tag['key']] = tag['value']

                events.append({"name": ev_name, "timestamp": ev_timestamp, "payload": ev})

        transformed_events = list(transform_event_json(event) for event in events)
        process_account_events_payload(self.connector.account, IngestionEventPayload(events=transformed_events))

    def poll_sentry_data(self):

        current_time = datetime.datetime.utcnow()
        start_time, end_time = self.get_polling_period_time_range(current_time)

        start_time_str, end_time_str = datetime.datetime.strftime(start_time,
                                                                  '%Y-%m-%dT%H:%M:%S'), datetime.datetime.strftime(
            end_time, '%Y-%m-%dT%H:%M:%S')

        for proj in self.projects:
            sentry_errors = self.get_user_level_sentry_errors(proj, start_time_str, end_time_str)
            self.create_events(sentry_errors)
