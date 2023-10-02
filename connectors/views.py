from datetime import datetime
from typing import Union

import pytz
from django.core.mail import send_mail

from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string

from django.db.utils import IntegrityError

from google.protobuf.wrappers_pb2 import BoolValue

from accounts.models import Account, get_request_account, get_request_user, User
from protos.event.api_pb2 import CreateConnectorRequest, CreateConnectorResponse, Message, RequestConnectorAPIRequest, \
    RequestConnectorAPIResponse, CreateTransformerMappingRequest, CreateTransformerMappingResponse, \
    GetConnectorKeysRequest, GetConnectorKeysResponse, SaveConnectorKeysResponse, SaveConnectorKeysRequest
from connectors.models import Connector, ConnectorKey, ConnectorRequest, TransformerMapping

from protos.event.connectors_pb2 import Connector as ConnectorProto, ConnectorKey as ConnectorKeyProto, ConnectorType, \
    DecoderType, TransformerType
from prototype.utils.decorators import web_api

from utils.proto_utils import proto_to_dict


@web_api(RequestConnectorAPIRequest)
def connectors_request(request_message: RequestConnectorAPIRequest) -> Union[
    RequestConnectorAPIResponse, HttpResponse]:
    account: Account = get_request_account()
    user: User = get_request_user()

    connector_type: ConnectorType = request_message.connector_type

    if not connector_type or connector_type == ConnectorType.UNKNOWN:
        return RequestConnectorAPIResponse(success=BoolValue(value=False),
                                           message=Message(title="Invalid Connector Request",
                                                           description="Input Connector not supported yet"))

    connectors_request, created = ConnectorRequest.objects.get_or_create(account=account,
                                                                         connector_type=connector_type,
                                                                         defaults={
                                                                             'account': account,
                                                                             'connector_type': connector_type,
                                                                         })

    if not created:
        return RequestConnectorAPIResponse(success=BoolValue(value=False), message=Message(title="Duplicate Request",
                                                                                           description="Connector already requested"))

    connector_name = ''
    for k, v in ConnectorType.items():
        if connector_type == v:
            connector_name = k
            break

    recipient_email_id = user.email
    timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S %d-%m-%Y")
    msg_html = render_to_string('connector_reqeust_email_template.html',
                                {'connector_type': connector_name.capitalize(),
                                 'user_name': recipient_email_id,
                                 'timestamp': timestamp})
    send_mail(
        subject="Connector Request",
        message="test",
        from_email=None,
        recipient_list=[recipient_email_id, "dipesh@drdroid.io", "siddarth@drdroid.io"],
        html_message=msg_html
    )

    return RequestConnectorAPIResponse(success=BoolValue(value=True))


@web_api(CreateConnectorRequest)
def connectors_create(request_message: CreateConnectorRequest) -> Union[
    CreateConnectorResponse, HttpResponse]:
    account: Account = get_request_account()

    connector: ConnectorProto = request_message.connector
    connector_type = connector.type
    connector_keys = request_message.connector_keys

    if connector_type == ConnectorType.SENTRY:
        config = proto_to_dict(connector.sentry_config)

    try:
        with transaction.atomic():
            db_connector = Connector(account=account,
                                     name=connector.name.value,
                                     connector_type=connector_type,
                                     is_active=connector.is_active.value,
                                     metadata=config)
            db_connector.save()

            for c_key in connector_keys:
                connector_key: ConnectorKeyProto = c_key
                db_connector_key = ConnectorKey(account=account,
                                                connector=db_connector,
                                                key_type=connector_key.key_type,
                                                key=connector_key.key.value,
                                                is_active=connector_key.is_active.value)
                db_connector_key.save()
    except IntegrityError:
        return CreateConnectorResponse(success=BoolValue(value=False),
                                       message=Message(title='Failed to create connector'))

    return CreateConnectorResponse(success=BoolValue(value=True))


@web_api(CreateTransformerMappingRequest)
def transformer_mapping_create(request_message: CreateTransformerMappingRequest) -> Union[
    CreateTransformerMappingResponse, HttpResponse]:
    account: Account = get_request_account()

    if request_message.account_id.value:
        account = Account.objects.get(id=request_message.account_id.value)
    decoder_type: DecoderType = request_message.decoder_type
    transformer_type: TransformerType = request_message.transformer_type

    try:
        with transaction.atomic():
            db_transformer_mapping = TransformerMapping(account=account,
                                                        decoder_type=decoder_type,
                                                        transformer_type=transformer_type,
                                                        is_active=True)
            db_transformer_mapping.save()
    except IntegrityError:
        return CreateConnectorResponse(success=BoolValue(value=False),
                                       message=Message(title='Failed to create transformer mapping'))

    return CreateTransformerMappingResponse(success=BoolValue(value=True))


@web_api(GetConnectorKeysRequest)
def get_keys(request_message: GetConnectorKeysRequest) -> Union[
    GetConnectorKeysResponse, HttpResponse]:
    account: Account = get_request_account()

    connector_type: ConnectorType = request_message.connector_type

    if not connector_type or connector_type == ConnectorType.UNKNOWN:
        return GetConnectorKeysResponse(connector_keys=[])

    connector_keys = ConnectorKey.objects.filter(account=account, connector__connector_type=connector_type, is_active=True)
    connector_key_protos = list(x.get_proto() for x in connector_keys)

    return GetConnectorKeysResponse(connector_keys=connector_key_protos)


@web_api(GetConnectorKeysRequest)
def delete_keys(request_message: GetConnectorKeysRequest) -> Union[
    GetConnectorKeysResponse, HttpResponse]:
    account: Account = get_request_account()

    connector_type: ConnectorType = request_message.connector_type

    if not connector_type or connector_type == ConnectorType.UNKNOWN:
        return GetConnectorKeysResponse(message='Connector Type not found')

    ConnectorKey.objects.filter(account=account, connector__connector_type=connector_type, is_active=True).delete()
    return GetConnectorKeysResponse(message='Connector Keys Deleted')


@web_api(SaveConnectorKeysRequest)
def save_keys(request_message: SaveConnectorKeysRequest) -> Union[
    SaveConnectorKeysResponse, HttpResponse]:
    account: Account = get_request_account()

    connector_type: ConnectorType = request_message.connector_type
    connector_keys = request_message.connector_keys

    if not connector_type or connector_type == ConnectorType.UNKNOWN:
        return SaveConnectorKeysResponse(message='Connector Type not found')

    try:
        conn = Connector.objects.get(account=account, connector_type=connector_type, is_active=True)
    except Connector.DoesNotExist:
        conn = Connector.objects.create(account=account, connector_type=connector_type, is_active=True, metadata={"connector_type": connector_type})

    for conn_key in connector_keys:
        try:
            c_key = ConnectorKey.objects.get(account=account, connector=conn, is_active=True, key_type=conn_key.key_type)
            c_key.key = conn_key.key.value
            c_key.save()
        except ConnectorKey.DoesNotExist:
            c_key = ConnectorKey.objects.create(account=account, connector=conn, is_active=True, key_type=conn_key.key_type, key=conn_key.key.value)

    return SaveConnectorKeysResponse(message='Keys saved')