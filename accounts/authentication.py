from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework import exceptions, HTTP_HEADER_ENCODING
from rest_framework.authentication import TokenAuthentication

from accounts.cache import GLOBAL_ACCOUNT_API_TOKEN_CACHE
from accounts.models import AccountApiToken, AccountApiTokenUser
from prototype.utils.headers import X_REQUEST_AWS_FIREHOSE
from prototype.utils.utils import build_absolute_uri


class AccountApiTokenAuthentication(TokenAuthentication):
    model = AccountApiToken
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        token = GLOBAL_ACCOUNT_API_TOKEN_CACHE.get(api_key=key)
        return AccountApiTokenUser(token.account_id), token


class AwsKinesisApiTokenAuthentication(AccountApiTokenAuthentication):
    def authenticate(self, request):
        request_firehose_access_header = request.headers[X_REQUEST_AWS_FIREHOSE]

        if not request_firehose_access_header:
            raise exceptions.AuthenticationFailed(f'Missing {X_REQUEST_AWS_FIREHOSE} header')

        auth = request_firehose_access_header
        if isinstance(request_firehose_access_header, str):
            # Work around django test client oddness
            auth = request_firehose_access_header.encode(HTTP_HEADER_ENCODING)

        auth = auth.split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided.')
        elif len(auth) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        try:
            token = auth[1].decode()
        except UnicodeError:
            raise exceptions.AuthenticationFailed(
                'Invalid token header. Token string should not contain invalid characters.')

        return self.authenticate_credentials(token)


def user_display(user):
    return user.email


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        location = settings.ACCOUNT_EMAIL_VERIFICATION_URL.format(emailconfirmation.key)
        protocol = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
        enabled = settings.EMAIL_USE_SITES
        if enabled:
            uri = build_absolute_uri(None, location, protocol, enabled)
        else:
            uri = build_absolute_uri(request, location, protocol, enabled)
        return uri

    def render_mail(self, template_prefix, email, context, headers=None):
        if not template_prefix == "account/email/email_confirmation_signup" or \
                template_prefix == "account/email/email_confirmation":
            return super().render_mail(template_prefix, email, context, headers)

        to = [email] if isinstance(email, str) else email
        subject = render_to_string("email_confirmation_subject.txt", context)
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        from_email = self.get_from_email()

        context["custom_user_name"] = context["user"].first_name + " " + context["user"].last_name

        text_body = render_to_string(
            "email_confirmation_message.txt",
            context,
            self.request,
        ).strip()

        html_body = render_to_string(
            "email_confirmation_message.html",
            context,
            self.request,
        ).strip()

        msg = EmailMultiAlternatives(subject, text_body, from_email, to, headers=headers)
        msg.attach_alternative(html_body, "text/html")
        return msg
