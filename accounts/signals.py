from allauth.account.signals import email_confirmed
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts import tasks
from accounts.models import User, Account, AccountApiToken
from prototype.utils.decorators import skip_signal


@receiver(post_save, sender=User)
@skip_signal()
def create_user_account(sender, instance, created, **kwargs):
    instance.skip_signal = True
    if not created:
        return
    if instance.account:
        return
    if instance.is_staff:
        return
    account = Account(owner=instance)
    account.save()
    print(f'Created account for user: {instance}')

    instance.account = account
    instance.save()
    print(f'Associated account for user: {instance}')
    tasks.setup_account.delay(account.id)
    print(f'Created account setup task for: {instance}')

    log_dict = {"msg": "Signup_New_User", "user_email": instance.email, "user_id": instance.id}
    print(log_dict)


@receiver(email_confirmed)
def generate_account_token_on_email_confirmed(request, email_address, **kwargs):
    user_model = get_user_model()
    try:
        user = user_model.objects.get(email=email_address)
        account = Account.objects.get(owner=user)
        token = AccountApiToken(account=account, created_by=user)
        token.save()
        print(f'Created account api token for account: {account}')
    except Exception as e:
        pass
