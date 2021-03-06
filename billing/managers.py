import stripe

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from billing.utils import (convert_tstamp, get_or_create_stripe_plan,
                           get_or_create_stripe_cus, get_or_create_stripe_sub,
                           get_or_create_stripe_charge)

# Create you managers here.


stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanManager(models.Manager):
    def create(self, name, amount, interval, description='', currency='usd',
               interval_count=1, metadata={}, statement_descriptor='',
               trial_period_days=0, **extra_fields):

        if not name:
            raise ValueError(_('Plans must have a name.'))
        elif not int(amount) >= 0:
            raise ValueError(_('Plans must have an amount, and the value must '
                               'be greater than 0.'))
        elif not interval:
            raise ValueError(_('Plans must have an interval.'))

        try:
            stripe_plan = get_or_create_stripe_plan(
                plan_id=None, name=name, amount=amount, interval=interval,
                currency=currency, interval_count=interval_count,
                metadata=metadata, statement_descriptor=statement_descriptor,
                trial_period_days=trial_period_days
            )
        except stripe.error.InvalidRequestError:
            return None

        plan = self.model(
            plan_id=stripe_plan['id'], name=stripe_plan['name'],
            description=description, amount=stripe_plan['amount'],
            interval=stripe_plan['interval'], currency=stripe_plan['currency'],
            interval_count=stripe_plan['interval_count'],
            statement_descriptor=statement_descriptor,
            trial_period_days=stripe_plan['trial_period_days'],
            **extra_fields
        )
        plan.save(using=self._db)
        return plan

    def active(self):
        return super(PlanManager, self).get_queryset().filter(is_active=True)


class CustomerManager(models.Manager):
    def create(self, user, account_balance, **extra_fields):

        if not user:
            raise ValueError(_('Customers must have a user.'))

        try:
            stripe_cu = get_or_create_stripe_cus(
                customer_id=None, account_balance=account_balance,
                description='Customer for {}'.format(user), email=user.email
            )
        except stripe.error.InvalidRequestError:
            return None

        cu = self.model(
            user=user, cu_id=stripe_cu['id'], account_balance=account_balance,
            currency=stripe_cu['currency'] if stripe_cu['currency'] else '',
            description=stripe_cu['description'], email=user.email,
            **extra_fields
        )
        cu.save(using=self._db)
        return cu


class SubscriptionManager(models.Manager):
    def create(self, customer, plan, metadata={}, trial_end=None, quantity=1,
               trial_period_days=0, **extra_fields):

        if not customer:
            raise ValueError(_('Subscriptions must have a customer.'))
        elif not plan:
            raise ValueError(_('Subscriptions must have a plan associated.'))

        try:
            stripe_sub = get_or_create_stripe_sub(
                subscription_id=None, customer=customer.cu_id,
                metadata=metadata, plan=plan.plan_id, quantity=quantity,
                trial_end=trial_end, trial_period_days=trial_period_days
            )
        except stripe.error.InvalidRequestError:
            return None

        sub = self.model(
            sub_id=stripe_sub['id'], customer=customer, plan=plan,
            status=stripe_sub['status'], trial_period_days=trial_period_days,
            trial_end=convert_tstamp(stripe_sub['trial_end']),
            trial_start=convert_tstamp(stripe_sub['trial_start']),
            cancel_at_period_end=stripe_sub['cancel_at_period_end'],
            canceled_at=convert_tstamp(stripe_sub['canceled_at']),
            current_period_end=convert_tstamp(stripe_sub['current_period_end']),
            current_period_start=convert_tstamp(stripe_sub['current_period_start']),
            ended_at=convert_tstamp(stripe_sub['ended_at']),
            start=convert_tstamp(stripe_sub['start']),
            **extra_fields)
        sub.save(using=self._db)
        return sub


class ChargeManager(models.Manager):
    def create(self, amount, source=None, currency='usd',
               description='', statement_descriptor='', receipt_email=None,
               **extra_fields):

        if not amount:
            raise ValueError(_('Charges must have an amount.'))

        try:
            descrip = statement_descriptor if statement_descriptor else None
            stripe_charge = get_or_create_stripe_charge(
                charge_id=None, amount=amount, currency=currency,
                description=description, receipt_email=receipt_email,
                source=source,
                statement_descriptor=descrip
            )
        except stripe.error.InvalidRequestError:
            return None

        charge = self.model(
            amount=amount, currency=currency, description=description,
            charge_id=stripe_charge['id'],
            amount_refunded=stripe_charge['amount_refunded'],
            paid=stripe_charge['paid'], disputed=stripe_charge['dispute'],
            refunded=stripe_charge['refunded'],
            captured=stripe_charge['captured'],
            statement_descriptor=statement_descriptor,
            charge_created=convert_tstamp(stripe_charge['created']),
            **extra_fields)
        charge.save(using=self._db)
        return charge
