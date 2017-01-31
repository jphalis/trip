import stripe

from datetime import date

from django.test import TestCase

from accounts.models import MyUser
from billing.models import Plan, Customer, Subscription
from ..utils import delete_stripe_plan
from ..utils import delete_stripe_cus
from ..utils import cancel_stripe_sub

# Create your utils tests here.


class StripeUnitTest(TestCase):

    def create_user(self):
        return MyUser.objects.create_user(
            email='test@user.com', first_name='John', last_name='Doe',
            password='pbkdf2_sha256$12000$64NIBRztT1eL$ip9P9F2vYdCvIXM')

    def create_customer(self):
        customer = Customer.objects.create(
            user=self.create_user(), account_balance=10000)
        cu = stripe.Customer.retrieve(customer.cu_id)
        cu.sources.create(source={
            'object': 'card',
            'number': '4242-4242-4242-4242',
            'exp_month': '08',
            'exp_year': '{}'.format(date.today().year + 1),
            'cvc': '111',
            'address_city': 'Hoboken',
            'address_line1': '1 Castle Point Terrace',
            'address_zip': '07030',
            'name': customer.user.get_full_name
        })
        return customer

    def create_plan(self):
        return Plan.objects.create(name='Test plan', amount=1000,
                                   interval='year', description='Test plan')

    def setUp(self):
        pass

    def test_create_and_delete_plan(self):
        plan = self.create_plan()
        self.assertTrue(plan is not None, 'Plan should be created.')

        deleted = delete_stripe_plan(plan.plan_id)
        self.assertTrue(deleted, 'Plan should be deleted.')

    def test_create_and_delete_customer(self):
        cu = self.create_customer()
        self.assertTrue(cu is not None, 'Customer should be created.')

        deleted = delete_stripe_cus(cu.cu_id)
        cu.delete()
        self.assertTrue(deleted, 'Customer should be deleted.')

    def test_create_and_delete_subscription(self):
        cu = self.create_customer()
        plan = self.create_plan()

        sub = Subscription.objects.create(customer=cu, plan=plan)
        self.assertTrue(sub is not None, 'Subscription should be created.')

        canceled = cancel_stripe_sub(sub.sub_id)
        self.assertTrue(canceled is not None, 'Subscription should be canceled.')

        deleted_cu = delete_stripe_cus(cu.cu_id)
        self.assertTrue(deleted_cu, 'Customer should be deleted.')

        deleted_plan = delete_stripe_plan(plan.plan_id)
        self.assertTrue(deleted_plan, 'Plan should be deleted.')
