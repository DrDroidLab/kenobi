python manage.py shell <<EOF
from accounts.models import User, AccountApiToken
from allauth.account.models import EmailAddress

user = User.objects.create_user(email='user@drdroid.io', password='password')
user_id = user.id
account_id = user.account_id

AccountApiToken.objects.create(account_id=account_id, created_by_id=user_id)

EmailAddress.objects.create(user_id=user_id, verified=True, primary=True, email=user.email)

# Exit the Python shell
exit()
EOF