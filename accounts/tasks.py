from celery import shared_task

from accounts.models import Account
from event.utils.account_data import setup_account_event_data
from utils.error_utils import error_dict


@shared_task
def setup_account(account_id: int):
    try:
        account = Account.objects.get(id=account_id)
        setup_account_event_data(account)
        return {'account_id': account_id, 'setup_status': 'SUCCESS'}
    except Account.DoesNotExist:
        return {'account_id': account_id, 'setup_status': 'FAILED', 'message': 'account setup failed',
                'error': f"account id:{account_id} doesn't exist"}
    except Exception as e:
        return {'account_id': account_id, 'setup_status': 'FAILED', **error_dict('account setup failed', e)}
