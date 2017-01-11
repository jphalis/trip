import stripe

from django.conf import settings
from django.utils.text import slugify

# Create you utilities here.


stripe.api_key = settings.STRIPE_SECRET_KEY


def get_or_create_stripe_plan(plan_id, name, amount, interval, currency='usd',
                              interval_count=1, metadata={},
                              statement_descriptor='',
                              trial_period_days=None):
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
    else:
        plan = stripe.Plan.create(
            id=slugify(name),
            name=name,
            amount=int(round(float(amount) * 100)),  # converted to cents,
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
    except stripe.error.InvalidRequestError:
        plan = None

    if plan:
        plan.delete()
        return True
    return False


def get_or_create_stripe_cus(customer_id, account_balance=None,
                             business_vat_id='', coupon=None,
                             default_source=None, description='', email=None,
                             metadata={}, shipping={}, source={}):

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
    else:
        cu = stripe.Customer.create(
            account_balance=account_balance, business_vat_id=business_vat_id,
            coupon=coupon, description=description, email=email,
            metadata=metadata, shipping=shipping, source=source
        )
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


def get_or_create_stripe_sub(subscription_id, customer,
                             application_fee_percent=None, coupon=None,
                             metadata={}, plan=None, prorate=None,
                             proation_date=None, quantity=1, source=None,
                             tax_percent=None, trial_end=None,
                             trial_period_days=None):
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
    else:
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


def get_or_create_stripe_invoice(invoice_id, customer_id, application_fee=None,
                                 closed=False, description='', forgiven=False,
                                 metadata={}, statement_descriptor='',
                                 subscription=None, tax_percent=None):
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
    else:
        invoice = stripe.Invoice.create(
            customer=customer_id,
            application_fee=application_fee,
            description=description,
            metadata=metadata,
            statement_descriptor=statement_descriptor,
            subscription=subscription,
            tax_percent=tax_percent
        )
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


def get_or_create_stripe_charge(charge_id, amount, currency='usd',
                                application_fee=None, capture=True,
                                description='', destination=None, metadata={},
                                fraud_details={}, receipt_email=None,
                                shipping={}, customer=None, source=None,
                                statement_descriptor=None):
    if not source or customer:
        raise ValueError('Charges must have a source or a customer.')

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
    else:
        charge = stripe.Charge.create(
            amount=int(round(float(amount) * 100)),  # converted to cents
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
    return charge
