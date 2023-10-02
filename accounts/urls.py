from dj_rest_auth.registration.views import VerifyEmailView, ResendEmailVerificationView, RegisterView
from dj_rest_auth.views import LoginView, LogoutView
from django.conf import settings
from django.urls import path, re_path
from django.views.generic import TemplateView

from accounts import views

accounturlpatterns = [
    # URLs that do not require a session or valid token
    path('login/', LoginView.as_view(), name='rest_login'),
    # URLs that require a user to be logged in with a valid session / token.
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('user/', views.get_user, name='rest_user_details'),
    path('signup/', RegisterView.as_view(), name='rest_signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='rest_verify_email'),
    path('resend-email/', ResendEmailVerificationView.as_view(), name="rest_resend_email"),

    re_path(
        r'^confirm-email-link/(?P<key>[-:\w]+)/$', views.confirm_email_link,
        name='account_confirm_email',
    ),
    path(
        'account-email-verification-sent/', TemplateView.as_view(),
        name='account_email_verification_sent',
    ),
]

if getattr(settings, 'REST_USE_JWT', False):
    from rest_framework_simplejwt.views import TokenVerifyView

    from dj_rest_auth.jwt_auth import get_refresh_view

    accounturlpatterns += [
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
        path('token/refresh/', get_refresh_view().as_view(), name='token_refresh'),
    ]

urlpatterns = [
    *accounturlpatterns,
    path('account_api_tokens', views.get_account_api_tokens),
    path('account_api_tokens/create', views.create_account_api_token),
    path('account_api_tokens/delete', views.delete_account_api_token),

    # path('registration/', include('dj_rest_auth.registration.urls')),
    # path('auth/', include('allauth.urls')),
]
