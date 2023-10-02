import useAxiosPrivate from './hooks/useAxiosPrivate';
import useTimeRange from './hooks/useTimeRange';
import { useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const defaultRequestHeaders = { 'Content-Type': 'application/json' };

const useApiCallback = () => {
  const { axiosPrivate } = useAxiosPrivate();
  const { timerange, getTimeRange } = useTimeRange();
  const { pathname } = useLocation();
  const navigate = useNavigate();

  const updateTimeRangeRequestData = useCallback(
    (setTimeRange, requestData) => {
      if (!setTimeRange || requestData === undefined) {
        return requestData;
      }
      if (requestData?.timeRange) {
        // IMPORTANT: check to mitigate race condition
        requestData.meta = {
          time_range: requestData?.timeRange
        };
        delete requestData.timeRange;
      } else {
        requestData['meta'] = {
          ...requestData?.meta,
          time_range: getTimeRange()
        };
      }
      return requestData;
    },
    [getTimeRange]
  );

  const callback = useCallback(
    (
      endpoint,
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      axiosPrivate
        .post(endpoint, updateTimeRangeRequestData(setTimeRange, requestData), {
          headers: { ...defaultRequestHeaders },
          withCredentials: true
        })
        .then(succ => {
          if (succ.status === 200 && succ.data.success === false) {
            throw new Error(succ?.data?.message?.description);
          }
          onSuccess(succ);
        })
        .catch(err => {
          let errObj = {};
          if (err?.response) {
            if (err?.response?.status && [400, 404].includes(err.response.status)) {
              errObj = {
                err: err.response.statusText,
                errorStatusCode: err.response.status
              };
            } else if (err?.response?.status === 500) {
              errObj = {
                err: 'Something went wrong',
                errorStatusCode: err.response.status
              };
            } else if (err?.response?.status === 401) {
              errObj = {
                err: 'Unauthorised',
                errorStatusCode: err?.response?.status
              };
            }
          } else {
            errObj = {
              err: err.message,
              errorStatusCode: 200
            };
          }
          onError(errObj);
          navigate(pathname, {
            state: errObj
          });
        });
    },
    [timerange, getTimeRange, axiosPrivate]
  );

  return callback;
};

const apis = {
  useGetEvents: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/events', requestData, onSuccess, onError, true);
    };

    return callback;
  },
  useGetEventTypeSummary: () => {
    const apiCallback = useApiCallback();
    const callback = (
      event_type_ids,
      page,
      searchPayload,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        event_type_ids: event_type_ids,
        meta: {
          page: page
        },
        fuzzy_search_request: searchPayload || null
      };
      apiCallback('/e/api/event_types/summary', requestData, onSuccess, onError);
    };

    return callback;
  },
  useFetchEventSearchOptions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/search/options/events', requestData, onSuccess, onError, true);
    };
    return callback;
  },

  useEventSearchFilter: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/events/search/v2', requestData, onSuccess, onError, true);
    };
    return callback;
  },

  useEventQuerySave: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/events/search/save', requestData, onSuccess, onError, true);
    };
    return callback;
  },

  useSaveMonitorQuery: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback(
        '/e/api/monitors/transactions/search/save',
        requestData,
        onSuccess,
        onError,
        true
      );
    };
    return callback;
  },

  useGetAlerts: () => {
    const apiCallback = useApiCallback();
    const callback = (
      page,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        meta: {
          page: page
        }
      };
      apiCallback('/e/api/alerts/summary', requestData, onSuccess, onError);
    };

    return callback;
  },
  useGetAlertDetailData: () => {
    const apiCallback = useApiCallback();
    const callback = (
      alert_id,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        meta: {
          // time_range: TIME_RANGE,
        },
        alert_id: parseInt(alert_id)
      };
      apiCallback('/e/api/alerts/details', requestData, onSuccess, onError, false);
    };

    return callback;
  },

  useGetDashboardData: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/dashboard_v1', requestData, onSuccess, onError, false);
    };

    return callback;
  },

  useSaveDashboardData: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/dashboard_v1/create_or_update', requestData, onSuccess, onError, false);
    };

    return callback;
  },

  useDeleteDashboardData: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/dashboard_v1/delete', requestData, onSuccess, onError, false);
    };

    return callback;
  },

  useDeactivateEntityTrigger: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/entities/triggers/inactivate', requestData, onSuccess, onError, false);
    };

    return callback;
  },

  useGetAlertMonitorTransactions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      alert_id,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        meta: {
          //   page: page
        },
        alert_id: parseInt(alert_id)
      };
      apiCallback('/e/api/alerts/monitor_transactions', requestData, onSuccess, onError);
    };

    return callback;
  },
  useGetAlertDetails: () => {
    const apiCallback = useApiCallback();
    const callback = (
      alert_id,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        meta: {
          // time_range: TIME_RANGE,
        },
        alert_id: parseInt(alert_id)
      };
      apiCallback('/e/api/alerts/details', requestData, onSuccess, onError, false);
    };

    return callback;
  },
  useGetEventTypeDefinition: () => {
    const apiCallback = useApiCallback();

    const callback = (
      // meta,
      event_type_ids,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        event_type_ids: event_type_ids
      };
      apiCallback('/e/api/event_types/definition', requestData, onSuccess, onError);
    };

    return callback;
  },
  useSearchEventKeys: () => {
    const apiCallback = useApiCallback();

    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/event_keys/search', requestData, onSuccess, onError);
    };

    return callback;
  },
  useCreateMonitors: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/monitors/create', requestData, onSuccess, onError);
    };

    return callback;
  },
  useCreateTriggers: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/monitors/triggers/create', requestData, onSuccess, onError);
    };

    return callback;
  },
  useUpdateTriggers: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/monitors/triggers/update', requestData, onSuccess, onError);
    };

    return callback;
  },

  useUpdateMonitors: () => {
    const apiCallback = useApiCallback();
    const callback = (requestData, onSuccess, onError) => {
      apiCallback('/e/api/monitors/update', requestData, onSuccess, onError);
    };

    return callback;
  },

  useFetchMonitorDefinition: () => {
    const apiCallback = useApiCallback();
    const callback = (
      monitor_ids,
      page,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        monitor_ids: monitor_ids,
        meta: {
          page: page
        }
      };
      apiCallback('/e/api/monitors/definition', requestData, onSuccess, onError);
    };

    return callback;
  },

  useGetMonitorTransactionSearch: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/monitors/transactions/search/v2', requestData, onSuccess, onError);
    };

    return callback;
  },

  useGetMonitorTransactionExport: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/monitors/transactions/export', requestData, onSuccess, onError);
    };

    return callback;
  },

  useMTSearchOptions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback(
        '/e/api/search/options/monitors/transactions/v2',
        requestData,
        onSuccess,
        onError
      );
    };

    return callback;
  },
  useGetMonitors: () => {
    const apiCallback = useApiCallback();
    const callback = (
      monitor_ids,
      page,
      searchPayload,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        monitor_ids: monitor_ids,
        meta: {
          page: page
        },
        fuzzy_search_request: searchPayload || null
      };
      apiCallback('/e/api/monitors', requestData, onSuccess, onError);
    };

    return callback;
  },
  useGetMonitorOptions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/monitors/options', {}, onSuccess, onError);
    };

    return callback;
  },
  useGetTriggerOptions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      monitor_id,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        monitor_id: monitor_id
      };
      apiCallback('/e/api/monitors/triggers/options', requestData, onSuccess, onError);
    };

    return callback;
  },

  useGetEntityTriggerOptions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      entity_id,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        entity_id: entity_id
      };
      apiCallback('/e/api/entities/triggers/options', requestData, onSuccess, onError);
    };

    return callback;
  },

  useCreateEntityTriggers: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/entities/triggers/create', requestData, onSuccess, onError);
    };

    return callback;
  },

  useUpdateEntityTriggers: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/entities/triggers/update', requestData, onSuccess, onError);
    };

    return callback;
  },

  useGetEntityTriggers: () => {
    const apiCallback = useApiCallback();
    const callback = (
      entity_id,
      page,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = false
    ) => {
      const requestData = {
        entity_id: entity_id,
        meta: {
          page: page
        }
      };
      apiCallback('/e/api/entities/triggers/get', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetEntityTriggersByTriggerId: () => {
    const apiCallback = useApiCallback();
    const callback = (
      entity_id,
      entity_trigger_id,
      page,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = false
    ) => {
      const requestData = {
        entity_id: entity_id,
        entity_trigger_id: entity_trigger_id,
        meta: {
          page: page
        }
      };
      apiCallback('/e/api/entities/triggers/get', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetMonitorsDefinition: () => {
    const apiCallback = useApiCallback();
    const callback = (
      monitor_ids,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        monitor_ids: monitor_ids
      };
      apiCallback('/e/api/monitors/definition', requestData, onSuccess, onError);
    };

    return callback;
  },
  useGetMonitorTransactions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      monitor_id,
      params,
      page,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      const requestData = {
        monitor_id: monitor_id,
        params: params,
        meta: {
          page: page
        }
      };
      apiCallback('/e/api/monitors/transactions', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },
  useGetTriggers: () => {
    const apiCallback = useApiCallback();
    const callback = (
      monitor_id,
      page,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = false
    ) => {
      const requestData = {
        monitor_id: monitor_id,
        meta: {
          page: page
        }
      };
      apiCallback('/e/api/monitors/triggers', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },
  useGetTriggersByTriggerId: () => {
    const apiCallback = useApiCallback();
    const callback = (
      trigger_id,
      page,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = false
    ) => {
      const requestData = {
        trigger_ids: [trigger_id],
        meta: {
          page: page
        }
      };
      apiCallback('/e/api/monitors/triggers', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },
  useGetMonitorsTransactionsEvents: () => {
    const apiCallback = useApiCallback();
    const callback = (
      transaction_id,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        transaction_id: transaction_id
      };
      apiCallback('/e/api/monitors/transactions/events', requestData, onSuccess, onError, false);
    };

    return callback;
  },

  useGetAccountApiToken: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/accounts/account_api_tokens', requestData, onSuccess, onError, false);
    };

    return callback;
  },

  useConnectorRequest: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/connectors/request', requestData, onSuccess, onError);
    };

    return callback;
  },

  useEntityCreateOptions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/entity/create/options', {}, onSuccess, onError, false);
    };

    return callback;
  },

  useCreateEntity: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/entity/create', requestData, onSuccess, onError);
    };

    return callback;
  },

  useUpdateEntity: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback('/e/api/entity/update', requestData, onSuccess, onError);
    };

    return callback;
  },

  useGetEntitySummary: () => {
    const apiCallback = useApiCallback();
    const callback = (
      entity_ids,
      page,
      searchPayload,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        entity_ids: entity_ids,
        meta: {
          page: page
        },
        fuzzy_search_request: searchPayload || null
      };
      apiCallback('/e/api/entity', requestData, onSuccess, onError);
    };

    return callback;
  },

  useGetEntityDetails: () => {
    const apiCallback = useApiCallback();
    const callback = (
      entity_id,
      page,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      const requestData = {
        entity_id: entity_id,
        meta: {
          page: page
        }
      };
      apiCallback('/e/api/entity/details', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetEntityInstanceSummary: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/e/api/entity/instances/search', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetEntitySearchOptions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      apiCallback(
        '/e/api/search/options/entity/instances/v2',
        requestData,
        onSuccess,
        onError,
        true
      );
    };
    return callback;
  },

  useGetInstanceDetails: () => {
    const apiCallback = useApiCallback();
    const callback = (
      entity_instance_id,
      page,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      const requestData = {
        entity_instance_id: entity_instance_id,
        meta: {
          page: page
        }
      };
      apiCallback('/e/api/entity/instances/details', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetMetricOptions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      context,
      id,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        context: context,
        id_literal: {
          type: 'LONG',
          long: id
        }
      };
      apiCallback('/e/api/metrics/options', requestData, onSuccess, onError, false);
    };

    return callback;
  },

  useGetGlobalMetricOptions: () => {
    const apiCallback = useApiCallback();
    const callback = (
      context,
      onSuccess,
      onError = e => {
        console.log(e);
      }
    ) => {
      const requestData = {
        context: context
      };
      apiCallback('/e/api/metrics/options', requestData, onSuccess, onError, false);
    };

    return callback;
  },

  useGetMetrics: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/e/api/metrics', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetEntityWorkflow: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/e/api/entity/workflow', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetFunnel: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/e/api/funnel', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetFunnelV2: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/e/api/funnel/v2', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetFunnelEditV2: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/e/api/entity_funnels/get', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetFunnelDropOff: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/e/api/funnel/drop_off', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useFunnelEventTypeDistribution: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback(
        '/e/api/funnel/drop_off_distribution/v2',
        requestData,
        onSuccess,
        onError,
        setTimeRange
      );
    };

    return callback;
  },
  useWorkflowBuilder: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/e/api/entity/build_workflow', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetWorkflowNodeMetrics: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback(
        '/e/api/entity/node_metrics_timeseries',
        requestData,
        onSuccess,
        onError,
        setTimeRange
      );
    };

    return callback;
  },

  useGetIntegrationKeys: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/connectors/get_keys', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useDeleteIntegrationKeys: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/connectors/delete_keys', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useSaveIntegrationKeys: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/connectors/save_keys', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useWorkflowBuilder: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/e/api/entity/build_workflow', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetFunnelV3: () => {
    const apiCallback = useApiCallback();
    const callback = (
      requestData,
      onSuccess,
      onError = e => {
        console.log(e);
      },
      setTimeRange = true
    ) => {
      apiCallback('/e/api/funnel/v3', requestData, onSuccess, onError, setTimeRange);
    };

    return callback;
  },

  useGetInstanceTimeline: () => {
    const apiCallback = useApiCallback();
    const callback = (
      entity_instance_id,
      page,
      onSuccess,
      onError = e => {
        console.log(e);
      },

      setTimeRange = false
    ) => {
      const requestData = {
        entity_instance_id: entity_instance_id,
        meta: {
          page: page
        }
      };
      apiCallback(
        '/e/api/entity/instances/timeline',
        requestData,
        onSuccess,
        onError,
        setTimeRange
      );
    };

    return callback;
  }
};

export default apis;
