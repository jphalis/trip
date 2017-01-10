import stripe

from datetime import timedelta

from django.conf import settings
from django.db.models.signals import post_save
from django.utils.text import slugify

from core.utils import rand_code_generator
from .models import Customer
from .signals import membership_dates_update


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_plan(name, amount, interval, currency='usd',
                       interval_count=1, metadata={},
                       statement_descriptor=None, trial_period_days=0):
    try:
        plan = stripe.Plan.create(
            id=slugify(name), name=name, amount=amount, interval=interval,
            interval_count=interval_count, metadata=metadata,
            statement_descriptor=statement_descriptor,
            trial_period_days=trial_period_days
        )
    except stripe.error.InvalidRequestError:
        plan = None
    return plan


def update_stripe_plan(plan_id, name=None, metadata={},
                       statement_descriptor=None, trial_period_days=0):
    try:
        plan = stripe.Plan.retrieve(plan_id)
    except stripe.error.InvalidRequestError:
        plan = None

    if plan:
        plan.name = name
        plan.metadata = metadata
        plan.statement_descriptor = statement_descriptor
        plan.trial_period_days = trial_period_days
        plan.save()
    return plan


def delete_stripe_plan(plan_id):
    try:
        plan = stripe.Plan.retrieve(plan_id)
    except stripe.error.InvalidRequestError:
        plan = None

    if plan:
        plan.delete()
        return True
    return False


def create_stripe_cus(account_balance=None, business_vat_id=None, coupon=None,
                      description=None, email=None, metadata={}, plan=None,
                      quantity=1, shipping={}, source=None, tax_percent=None,
                      trial_end=None):
    try:
        cus = stripe.Customer.create(
            account_balance=account_balance, business_vat_id=business_vat_id,
            coupon=coupon, description=description, email=email,
            metadata=metadata, plan=plan, quantity=quantity, shipping=shipping,
            source=source, tax_percent=tax_percent, trial_end=trial_end
        )
    except stripe.error.InvalidRequestError:
        cus = None
    return cus


def update_stripe_cus(customer_id, account_balance=None, business_vat_id=None,
                      coupon=None, default_source=None, description=None,
                      email=None, metadata={}, shipping={}, source=None):
    try:
        cu = stripe.Customer.retrieve(customer_id)
    except stripe.error.InvalidRequestError:
        cu = None

    if cu:
        cu.account_balance = account_balance
        cu.business_vat_id = business_vat_id
        cu.coupon = coupon
        cu.default_source = default_source
        cu.description = description
        cu.email = email
        cu.metadata = metadata
        cu.shipping = shipping
        cu.source = source
        cu.save()
    return cu


def delete_stripe_cus(customer_id):
    try:
        cu = stripe.Customer.retrieve(customer_id)
    except stripe.error.InvalidRequestError:
        cu = None

    if cu:
        cu.delete()
        return True
    return False


def create_stripe_sub(customer, application_fee_percent=None, coupon=None,
                      metadata={}, plan=None, quantity=1, source=None,
                      tax_percent=None, trial_end=None,
                      trial_period_days=None):
    try:
        sub = stripe.Subscription.create(
            customer=customer,
            application_fee_percent=application_fee_percent,
            coupon=coupon,
            metadata=metadata,
            plan=plan,
            quantity=quantity,
            source=source,
            tax_percent=tax_percent,
            trial_end=trial_end,
            trial_period_days=trial_period_days
        )
    except stripe.error.InvalidRequestError:
        sub = None
    return sub


def update_stripe_sub(subscription_id, application_fee_percent=None,
                      coupon=None, metadata={}, plan=None, prorate=None,
                      proation_date=None, quantity=1, source=None,
                      tax_percent=None, trial_end=None):
    try:
        sub = stripe.Subscription.retrieve(subscription_id)
    except stripe.error.InvalidRequestError:
        sub = None

    if sub:
        sub.application_fee_percent = application_fee_percent
        sub.coupon = coupon
        sub.metadata = metadata
        sub.plan = plan
        sub.prorate = prorate
        sub.proation_date = proation_date
        sub.quantity = quantity
        sub.source = source
        sub.tax_percent = tax_percent
        sub.trial_end = trial_end
        sub.save()
    return sub


def cancel_stripe_sub(subscription_id):
    try:
        sub = stripe.Subscription.retrieve(subscription_id)
    except stripe.error.InvalidRequestError:
        sub = None

    if sub:
        sub.delete()
        return True
    return False


def create_stripe_invoice(customer_id, application_fee=None, description=None,
                          metadata={}, statement_descriptor=None,
                          subscription=None, tax_percent=None):
    try:
        invoice = stripe.Invoice.create(
            customer=customer_id, application_fee=application_fee,
            description=description, metadata=metadata,
            statement_descriptor=statement_descriptor,
            subscription=subscription, tax_percent=tax_percent
        )
    except stripe.error.InvalidRequestError:
        invoice = None
    return invoice


def update_stripe_invoice(invoice_id, application_fee=None, closed=None,
                          description=None, forgiven=False, metadata={},
                          statement_descriptor=None, tax_percent=None):
    try:
        invoice = stripe.Invoice.retrieve(invoice_id)
    except stripe.error.InvalidRequestError:
        invoice = None

    if invoice:
        invoice.application_fee = application_fee
        invoice.closed = closed
        invoice.description = description
        invoice.forgiven = forgiven
        invoice.metadata = metadata
        invoice.statement_descriptor = statement_descriptor
        invoice.tax_percent = tax_percent
        invoice.save()
    return invoice


def delete_stripe_invoice(invoice_id):
    try:
        invoice = stripe.Invoice.retrieve(invoice_id)
    except stripe.error.InvalidRequestError:
        invoice = None

    if invoice:
        invoice.delete()
        return True
    return False


def create_stripe_charge(amount, currency='usd', application_fee=None,
                         capture=True, description=None, destination=None,
                         metadata={}, receipt_email=None, shipping={},
                         customer=None, source=None,
                         statement_descriptor=None):
    if not source or customer:
        raise ValueError('Charges must have a source or a customer.')

    try:
        charge = stripe.Charge.create(
            amount=int(round(float(amount) * 100)),  # converted to cents
            currency=currency, application_fee=application_fee,
            capture=capture, description=description, destination=destination,
            metadata=metadata, receipt_email=receipt_email, shipping=shipping,
            customer=customer, source=source,
            statement_descriptor=statement_descriptor
        )
    except stripe.error.CardError:
        charge = None
    except stripe.error.InvalidRequestError:
        charge = None
    return charge


def update_stripe_charge(charge_id, description=None, metadata={},
                         receipt_email=None, fraud_details={}, shipping={}):
    try:
        charge = stripe.Charge.retrieve(charge_id)
    except stripe.error.InvalidRequestError:
        charge = None

    if charge:
        charge.description = description
        charge.metadata = metadata
        charge.receipt_email = receipt_email
        charge.fraud_details = fraud_details
        charge.shipping = shipping
        charge.save()
    return charge
