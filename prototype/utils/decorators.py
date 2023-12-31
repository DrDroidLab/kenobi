import functools
from typing import Dict

from allauth.account.utils import has_verified_email
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from google.protobuf.wrappers_pb2 import BoolValue
from rest_framework.decorators import authentication_classes, api_view

from accounts.authentication import AccountApiTokenAuthentication, \
    AwsKinesisApiTokenAuthentication
from protos.event.api_pb2 import ErrorMessage, Message
from google.protobuf.message import Message as ProtoMessage
from prototype.threadlocal import get_current_request
from utils.error_utils import error_dict
from utils.proto_utils import json_to_proto, proto_to_dict


def skip_signal():
    def _skip_signal(signal_func):
        @functools.wraps(signal_func)
        def _decorator(sender, instance, **kwargs):
            if hasattr(instance, 'skip_signal'):
                return None
            return signal_func(sender, instance, **kwargs)

        return _decorator

    return _skip_signal


class ProtoJsonResponse(JsonResponse):
    def __init__(
            self,
            data,
            **kwargs,
    ):
        if not isinstance(data, ProtoMessage):
            raise TypeError(
                f"data must be an instance of google.protobuf.message.Message, not {type(data)}"
            )

        json_data: Dict = proto_to_dict(data)
        super().__init__(json_data, **kwargs)


def proto_schema_validator(request_schema):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request: HttpRequest):
            body = request.body
            try:
                if body:
                    request_message = json_to_proto(body, request_schema)
                else:
                    request_message = request_schema()
            except Exception as e:
                return JsonResponse(error_dict('Error while deserializing the proto msg', e), status=400,
                                    content_type='application/json')

            try:
                response = func(request_message)
                if isinstance(response, ProtoMessage):
                    return JsonResponse(proto_to_dict(response), status=200, content_type='application/json')
                elif isinstance(response, dict):
                    return JsonResponse(response, status=200, content_type='application/json')
                elif isinstance(response, HttpResponse):
                    return response
            except Exception as e:
                return JsonResponse(error_dict('Error while processing the request', e), status=500,
                                    content_type='application/json')

        return wrapper

    return decorator


def web_api(request_schema):
    def decorator(func):
        @functools.wraps(func)
        @csrf_exempt
        @api_view(['POST'])
        @authentication_classes([JWTCookieAuthentication])
        @login_required
        @proto_schema_validator(request_schema)
        def wrapper(message):
            return func(message)

        return wrapper

    return decorator


def check_user_email_verified(func):
    @functools.wraps(func)
    def _wrapped_view(message):
        user = get_current_request().user
        if not has_verified_email(user):
            return ProtoJsonResponse(
                ErrorMessage(
                    error=BoolValue(value=True),
                    message=Message(title='User email not verified')
                ),
                status=200
            )
        return func(message)

    return _wrapped_view


def api_auth_check(func):
    @functools.wraps(func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return HttpResponse(status=401)

    return _wrapped_view


def account_data_api(request_schema):
    def decorator(func):
        @functools.wraps(func)
        @csrf_exempt
        @api_view(['POST'])
        @authentication_classes([AccountApiTokenAuthentication])
        @api_auth_check
        @proto_schema_validator(request_schema)
        def wrapper(message):
            return func(message)

        return wrapper

    return decorator


def aws_kinesis_data_api(request_schema):
    def decorator(func):
        @functools.wraps(func)
        @csrf_exempt
        @api_view(['POST'])
        @authentication_classes([AwsKinesisApiTokenAuthentication])
        @api_auth_check
        @proto_schema_validator(request_schema)
        def wrapper(message):
            return func(message)

        return wrapper

    return decorator
