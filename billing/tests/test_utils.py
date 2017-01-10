import stripe

from django.conf import settings
from django.test import TestCase

# Create your utils tests here.


stripe.api_key = settings.STRIPE_API_KEY


def create_user():
    from accounts.models import MyUser

    return MyUser.objects.create_user(
        email='test@user.com', first_name='John', last_name='Doe',
        password='pbkdf2_sha256$12000$64NIBRztT1eL$ip9P9F2vYdCvIXM')


def create_customer():
    from billing.models import Customer

    return Customer.objects.create(
        user=create_user(), account_balance=100.00, plan_id='???',
        subscription_id='???')


class SomeUnitTest(TestCase):

    def setUp(self):
        self.customer = self.create_customer()
