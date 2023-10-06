python manage.py shell <<EOF
from accounts.models import User, AccountApiToken, Account
from allauth.account.models import EmailAddress

user = User.objects.create_superuser(email='user@drdroid.io', password='password')
user_id = user.id
account_id = user.account_id

Account.objects.filter(id=account_id).update(is_whitelisted=True)
AccountApiToken.objects.create(account_id=account_id, created_by_id=user_id)
EmailAddress.objects.create(user_id=user_id, verified=True, primary=True, email=user.email)

from django_celery_beat.models import PeriodicTask, IntervalSchedule
one_minute_sc = IntervalSchedule.objects.create(every=1, period='minutes')
ten_minute_sc = IntervalSchedule.objects.create(every=10, period='minutes')

PeriodicTask.objects.create(name='1 minute schedule', task='event.tasks.missing_event_trigger_cron', interval=one_minute_sc, args='[60]')
PeriodicTask.objects.create(name='10 minute schedule', task='event.tasks.delayed_event_trigger_cron', interval=one_minute_sc, args='[600]')

# Exit the Python shell
exit()
EOF