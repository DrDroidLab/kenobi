import json
import math

import requests
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi

from datadog_api_client.v2.api.metrics_api import MetricsApi as MetricsApi2
from datadog_api_client.v2.model.formula_limit import FormulaLimit
from datadog_api_client.v2.model.metrics_data_source import MetricsDataSource
from datadog_api_client.v2.model.metrics_timeseries_query import MetricsTimeseriesQuery
from datadog_api_client.v2.model.query_formula import QueryFormula
from datadog_api_client.v2.model.timeseries_formula_query_request import TimeseriesFormulaQueryRequest
from datadog_api_client.v2.model.timeseries_formula_request import TimeseriesFormulaRequest
from datadog_api_client.v2.model.timeseries_formula_request_attributes import TimeseriesFormulaRequestAttributes
from datadog_api_client.v2.model.timeseries_formula_request_queries import TimeseriesFormulaRequestQueries
from datadog_api_client.v2.model.timeseries_formula_request_type import TimeseriesFormulaRequestType

from connectors.models import Connector, ConnectorKey
from protos.event.connectors_pb2 import ConnectorType
from protos.event.connectors_pb2 import ConnectorKey as ConnectorKeyProto




class DatadogConnector(object):
    def __init__(self, tr, account_id):
        self.start_time = tr.time_geq
        self.end_time = tr.time_lt
        try:
            self.dd_connector = Connector.objects.get(account_id=account_id, connector_type=ConnectorType.DATADOG, is_active=True)
            self.dd_connector_keys = ConnectorKey.objects.filter(account_id=account_id, connector_id=self.dd_connector.id, is_active=True)
            self.configuration = Configuration()
            self.configuration.api_key["apiKeyAuth"] = self.dd_connector_keys.get(key_type=ConnectorKeyProto.DATADOG_API_KEY).key
            self.configuration.api_key["appKeyAuth"] = self.dd_connector_keys.get(key_type=ConnectorKeyProto.DATADOG_APP_KEY).key
        except Connector.DoesNotExist:
            raise Exception("Datadog connector not found")
        except ConnectorKey.DoesNotExist:
            raise Exception("Datadog connector keys not found")

    def fetch_metric(self, metric, tr=None):
        with ApiClient(self.configuration) as api_client:
            api_instance = MetricsApi(api_client)

            s_time, e_time = self.start_time, self.end_time
            if tr:
                s_time, e_time = tr.time_geq, tr.time_lt

            time_duration = e_time - s_time

            metric_type = metric.split(':')[0]
            metric = metric + '.rollup({}, {})'.format(metric_type, time_duration)

            response = api_instance.query_metrics(s_time, e_time, metric)

            series = response.get('series', [])
            if len(series) > 0:
                pointlist = series[0].get('pointlist', [])
                aggr = series[0].get('aggr', 'avg')
                unit = series[0].get('unit', [])[0]['short_name']
                if not unit:
                    unit = ''
                if aggr == 'sum':
                    return {"value": round(sum(list(x._data_store['value'][1] for x in pointlist))), "unit": unit}
                else:
                    return {"value": round(sum(list(x._data_store['value'][1] for x in pointlist)) / len(pointlist), 2), "unit": unit}
            return {}


    def fetch_metric_timeseries(self, metric, tr=None):
        s_time, e_time = self.start_time, self.end_time
        if tr:
            s_time, e_time = tr.time_geq, tr.time_lt

        resolution = math.ceil((e_time - s_time) / 15 / 60) * 60

        body = {
            "data": {
                "attributes": {
                    "from": s_time*1000,
                    "interval": resolution*1000,
                    "queries": [
                        {
                            "data_source": "metrics",
                            "query": metric
                        }
                    ],
                    "to": e_time*1000
                },
                "type": "timeseries_request"
            }
        }

        url = 'https://api.datadoghq.com/api/v2/query/timeseries'
        headers = {"DD-API-KEY": self.configuration.api_key["apiKeyAuth"], "DD-APPLICATION-KEY": self.configuration.api_key["appKeyAuth"], "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(body))

        response = response.json()

        times = response.get('data', {}).get('attributes', {}).get('times', [])
        values = response.get('data', {}).get('attributes', {}).get('values', [])
        if len(times) > 0:
            pointlist = values[0]
            series = []
            for idx, x in enumerate(times):
                series.append({'timestamp': x, 'value': pointlist[idx]})
            return {"series": series, "unit": ''}
        return {"series": [], "unit": ''}