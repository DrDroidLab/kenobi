from newrelic_api import Applications
import datetime

from connectors.models import Connector, ConnectorKey
from protos.event.connectors_pb2 import ConnectorType
from protos.event.connectors_pb2 import ConnectorKey as ConnectorKeyProto

def format_dt(ts):
    dt_object = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    return dt_object

class NewRelicConnector(object):
    def __init__(self, tr, account_id):
        self.start_time = tr.time_geq
        self.end_time = tr.time_lt
        try:
            self.nr_connector = Connector.objects.get(account_id=account_id, connector_type=ConnectorType.NEW_RELIC, is_active=True)
            self.nr_connector_keys = ConnectorKey.objects.filter(account_id=account_id, connector_id=self.nr_connector.id, is_active=True)
            self.app = Applications(api_key=self.nr_connector_keys.get(key_type=ConnectorKeyProto.NEWRELIC_API_KEY).key)
            self.app_id = self.nr_connector_keys.get(key_type=ConnectorKeyProto.NEWRELIC_APP_ID).key
        except Connector.DoesNotExist:
            raise Exception("NewRelic connector not found")
        except ConnectorKey.DoesNotExist:
            raise Exception("NewRelic connector keys not found")

    def fetch_metric(self, metric, tr=None):
        metric_tokens = metric.split(":")
        metric_type = metric_tokens[0]
        metric_name = metric_tokens[1]

        s_time, e_time = self.start_time, self.end_time
        if tr:
            s_time, e_time = tr.time_geq, tr.time_lt

        metric_response = self.app.metric_data(self.app_id, [metric_name], values=[metric_type], from_dt=format_dt(s_time), to_dt=format_dt(e_time), summarize=True)

        series = metric_response.get('metric_data', {}).get('metrics', [])[0].get('timeslices', [])
        if len(series) > 0:
            metric_values = series[0].get('values', {})
            metric_value = metric_values.get(metric_type, None)
            unit = ''
            return {"value": round(metric_value, 2), "unit": unit}
        return {}

    def fetch_metric_timeseries(self, metric, tr=None):
        metric_tokens = metric.split(":")
        metric_type = metric_tokens[0]
        metric_name = metric_tokens[1]

        s_time, e_time = self.start_time, self.end_time
        if tr:
            s_time, e_time = tr.time_geq, tr.time_lt

        metric_response = self.app.metric_data(self.app_id, [metric_name], values=[metric_type], from_dt=format_dt(s_time), to_dt=format_dt(e_time), summarize=False)

        series = metric_response.get('metric_data', {}).get('metrics', [])[0].get('timeslices', [])
        if len(series) > 0:
            return {"series": series, "unit": '', "metric_type": metric_type}
        return {"series": [], "unit": '', "metric_type": ''}
