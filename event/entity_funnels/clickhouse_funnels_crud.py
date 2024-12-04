from accounts.models import Account
from event.cache import GLOBAL_PANEL_CACHE
from event.entity_funnels.entity_funnels_crud import EntityFunnelCrudIncorrectPayloadException
from event.workflows.funnel import Funnel
from protos.event.entity_pb2 import WorkflowView
from protos.event.panel_pb2 import PanelV1, PanelData
from utils.proto_utils import dict_to_proto

start_node_conn_types = [WorkflowView.NodeConnectionType.OUT]
mid_node_conn_types = [WorkflowView.NodeConnectionType.IN, WorkflowView.NodeConnectionType.OUT]
end_node_conn_types = [WorkflowView.NodeConnectionType.IN]