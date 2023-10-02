from typing import Union

from allauth.account.models import EmailConfirmationHMAC, EmailConfirmation
from django.http import HttpResponse, HttpRequest, Http404
from django.views.decorators.csrf import csrf_exempt
from google.protobuf.wrappers_pb2 import BoolValue

from accounts.models import get_request_account, Account, AccountApiToken
from accounts.utils import is_request_user_email_verified
from protos.event.api_pb2 import GetAccountApiTokensRequest, GetAccountApiTokensResponse, \
    CreateAccountApiTokenRequest, CreateAccountApiTokenResponse, DeleteAccountApiTokenRequest, \
    DeleteAccountApiTokenResponse, GetUserRequest, GetUserResponse
from prototype.threadlocal import get_current_request
from prototype.utils.decorators import web_api
from prototype.utils.meta import get_meta
from prototype.utils.queryset import filter_page


@web_api(GetAccountApiTokensRequest)
def get_account_api_tokens(request_message: GetAccountApiTokensRequest) -> Union[
    GetAccountApiTokensResponse, HttpResponse]:
    if not is_request_user_email_verified():
        return GetAccountApiTokensResponse(meta=get_meta(), account_api_tokens=[])

    account: Account = get_request_account()
    qs = account.account_api_token.all()

    total_count = qs.count()
    page = request_message.meta.page
    account_api_tokens = [account_api_token.proto for account_api_token in
                          filter_page(qs.order_by("-created_at"), page)]

    return GetAccountApiTokensResponse(
        meta=get_meta(page=page, total_count=total_count),
        account_api_tokens=account_api_tokens)


@web_api(CreateAccountApiTokenRequest)
def create_account_api_token(request_message: CreateAccountApiTokenRequest) -> Union[
    CreateAccountApiTokenResponse, HttpResponse]:
    if not is_request_user_email_verified():
        return CreateAccountApiTokenResponse(success=BoolValue(value=False))

    user = get_current_request().user
    account: Account = get_request_account()

    api_token = AccountApiToken(account=account, created_by=user)
    api_token.save()
    return CreateAccountApiTokenResponse(success=BoolValue(value=True), account_api_token=api_token.proto)


@web_api(DeleteAccountApiTokenRequest)
def delete_account_api_token(request_message: DeleteAccountApiTokenRequest) -> Union[
    DeleteAccountApiTokenResponse, HttpResponse]:
    if not is_request_user_email_verified():
        return DeleteAccountApiTokenResponse(success=BoolValue(value=False))

    account: Account = get_request_account()
    key: str = request_message.account_api_token_key
    if key == "":
        return DeleteAccountApiTokenResponse(success=BoolValue(value=False))
    try:
        api_token = AccountApiToken.objects.get(key=key, account=account)
    except AccountApiToken.DoesNotExist:
        return DeleteAccountApiTokenResponse(success=BoolValue(value=False))

    api_token.delete()
    return DeleteAccountApiTokenResponse(success=BoolValue(value=True))


@csrf_exempt
def confirm_email_link(request: HttpRequest, key):
    email_confirmation = EmailConfirmationHMAC.from_key(key)
    if not email_confirmation:
        queryset = EmailConfirmation.objects.all_valid()
        queryset = queryset.select_related("email_address__user")
        try:
            email_confirmation = queryset.get(key=key.lower())
        except EmailConfirmation.DoesNotExist:
            raise Http404()
    email_confirmation.confirm(request)
    return HttpResponse({'success': True})


@web_api(GetUserRequest)
def get_user(request_message: GetUserRequest) -> Union[GetUserResponse, HttpResponse]:
    request = get_current_request()
    user = request.user
    return GetUserResponse(user=user.proto)
