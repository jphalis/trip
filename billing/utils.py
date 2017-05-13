import stripe

from datetime import datetime

from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

# Create you utilities here.


stripe.api_key = settings.STRIPE_SECRET_KEY


def convert_tstamp(timestamp):
    return datetime.fromtimestamp(timestamp) if timestamp else None


def get_or_create_stripe_plan(plan_id, name, amount, interval, currency='usd',
                              interval_count=1, metadata={},
                              statement_descriptor=None,
                              trial_period_days=0):
    try:
        plan = stripe.Plan.retrieve(plan_id)
        plan.plan = plan_id
        plan.name = name
        plan.metadata = metadata
        if statement_descriptor == '':
            statement_descriptor = None
        plan.statement_descriptor = statement_descriptor
        plan.trial_period_days = trial_period_days
        plan.save()
    except stripe.error.InvalidRequestError:
        plan = stripe.Plan.create(
            id=slugify(name),
            name=name,
            amount=amount,
            interval=interval,
            currency=currency,
            interval_count=interval_count,
            metadata=metadata,
            statement_descriptor=statement_descriptor,
            trial_period_days=trial_period_days
        )
    return plan


def delete_stripe_plan(plan_id):
    try:
        plan = stripe.Plan.retrieve(plan_id)
        plan.delete()
        return True
    except stripe.error.InvalidRequestError:
        return False


def get_or_create_stripe_cus(customer_id, account_balance=0, description=None,
                             email=None, metadata={}, shipping={}, source={}):

    try:
        cu = stripe.Customer.retrieve(customer_id)
        if account_balance > 0:
            cu.account_balance = account_balance
        cu.description = description
        cu.email = email
        cu.metadata = metadata
        cu.shipping = shipping
        cu.source = source
        cu.save()
    except stripe.error.InvalidRequestError:
        cu = stripe.Customer.create(
            account_balance=account_balance, description=description,
            email=email, metadata=metadata, shipping=shipping, source=source
        )
    return cu


def delete_stripe_cus(customer_id):
    try:
        cu = stripe.Customer.retrieve(customer_id)
        cu.delete()
        return True
    except stripe.error.InvalidRequestError:
        return False


def get_or_create_stripe_sub(subscription_id, customer, metadata={}, plan=None,
                             quantity=1, source={}, trial_end=None,
                             trial_period_days=0):
    try:
        sub = stripe.Subscription.retrieve(subscription_id)
        sub.metadata = metadata
        sub.plan = plan
        sub.quantity = quantity
        sub.source = source
        sub.save()
    except stripe.error.InvalidRequestError:
        sub = stripe.Subscription.create(
            customer=customer,
            metadata=metadata,
            plan=plan,
            quantity=quantity,
            source=source,
            trial_end=trial_end,
            trial_period_days=trial_period_days
        )
    return sub


def cancel_stripe_sub(subscription_id, at_period_end=False):
    try:
        sub = stripe.Subscription.retrieve(subscription_id)
        sub.delete(at_period_end=at_period_end)
    except stripe.error.InvalidRequestError:
        sub = None
    return sub


def get_or_create_stripe_charge(charge_id, amount, currency='usd',
                                application_fee=None, capture=True,
                                description=None, destination=None,
                                metadata={}, fraud_details={},
                                receipt_email=None, shipping={}, customer=None,
                                source={}, statement_descriptor=None):
    if not source and not customer:
        raise ValueError(_('Charges must have a source or a customer.'))

    try:
        charge = stripe.Charge.retrieve(charge_id)
        charge.description = description
        charge.metadata = metadata
        charge.receipt_email = receipt_email
        charge.fraud_details = fraud_details
        charge.shipping = shipping
        charge.save()
    except stripe.error.InvalidRequestError:
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency=currency,
                application_fee=application_fee,
                capture=capture,
                description=description,
                destination=destination,
                metadata=metadata,
                receipt_email=receipt_email,
                shipping=shipping,
                customer=customer,
                source=source,
                statement_descriptor=statement_descriptor
            )
        except stripe.CardError:
            charge = None
    return charge
