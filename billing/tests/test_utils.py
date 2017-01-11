from django.test import TestCase

from accounts.models import MyUser
from billing.models import Customer
from ..utils import get_or_create_stripe_plan, delete_stripe_plan
from ..utils import get_or_create_stripe_cus, delete_stripe_cus
from ..utils import get_or_create_stripe_sub, delete_stripe_sub

# Create your utils tests here.


class StripeUnitTest(TestCase):

    def create_user():
        return MyUser.objects.create_user(
            email='test@user.com', first_name='John', last_name='Doe',
            password='pbkdf2_sha256$12000$64NIBRztT1eL$ip9P9F2vYdCvIXM')

    def create_customer(self):
        return Customer.objects.create(
            user=self.create_user(), account_balance=100.00)

    def setUp(self):
        self.customer = self.create_customer()

    def test_create_and_delete_plan(self):
        plan = get_or_create_stripe_plan(plan_id=None, name="Test plan",
                                         amount=10, interval='year')
        self.assertTrue(plan is not None, 'Plan should be created.')

        deleted = delete_stripe_plan(plan['id'])
        self.assertTrue(deleted, 'Plan should be deleted.')

    def test_create_and_delete_customer(self):
        cu = get_or_create_stripe_cus(customer_id=None)
        self.assertTrue(cu is not None, 'Customer should be created.')

        deleted = delete_stripe_cus(cu['id'])
        self.assertTrue(deleted, 'Customer should be deleted.')

    def test_create_and_delete_subscription(self):
        pass
        # sub = get_or_create_stripe_sub()
        # self.assertTrue(sub is not None, 'Subscription should be created.')

        # deleted = delete_stripe_sub(sub['id'])
        # self.assertTrue(deleted, 'Subscription should be deleted.')



    #     self.assertEqual(expected_result, actual_result, 'Expected result: '
    #         '{} did not match actual result: {}'.format(expected_result,
    #                                                     actual_result))
