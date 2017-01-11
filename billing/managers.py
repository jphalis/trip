import stripe

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from billing.utils import (get_or_create_stripe_plan, get_or_create_stripe_cus,
                           get_or_create_stripe_sub,
                           get_or_create_stripe_charge)

# Create you managers here.


stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanManager(models.Manager):
    def create(self, name, amount, interval, currency='usd',
               interval_count=1, metadata={}, statement_descriptor='',
               trial_period_days=None, **extra_fields):

        if not name:
            raise ValueError('Plans must have a name.')
        elif not amount:
            raise ValueError('Plans must have an amount.')
        elif not interval:
            raise ValueError('Plans must have an interval.')

        try:
            stripe_plan = get_or_create_stripe_plan(
                plan_id=None,
                name=name,
                amount=amount,
                interval=interval,
                currency=currency,
                interval_count=interval_count,
                metadata=metadata,
                statement_descriptor=statement_descriptor,
                trial_period_days=trial_period_days
            )
        except stripe.error.InvalidRequestError as e:
            print e
            return None

        plan = self.model(
            plan_id=stripe_plan['id'],
            name=stripe_plan['name'],
            amount=amount,
            interval=stripe_plan['interval'],
            currency=stripe_plan['currency'],
            interval_count=stripe_plan['interval_count'],
            metadata=stripe_plan['metadata'],
            statement_descriptor=statement_descriptor,
            trial_period_days=stripe_plan['trial_period_days'],
            **extra_fields
        )
        plan.save(using=self._db)
        return plan


class CustomerManager(models.Manager):
    def create(self, user, account_balance,
               end_date=timezone.now() + timedelta(days=365), **extra_fields):

        if not user:
            raise ValueError('Customers must have a user.')
        elif not account_balance:
            raise ValueError('Customers must have an account balance.')

        try:
            stripe_cu = get_or_create_stripe_cus(
                customer_id=None, account_balance=account_balance,
                description='Customer for {}'.format(user), email=user.email
            )
        except stripe.error.InvalidRequestError as e:
            print e
            return None

        cu = self.model(
            user=user,
            cu_id=stripe_cu['id'],
            account_balance=account_balance,
            business_vat_id='',
            currency=stripe_cu['currency'],
            default_source='',
            description=stripe_cu['description'],
            email=user.email,
            end_date=end_date,
            **extra_fields
        )
        cu.save(using=self._db)
        return cu


class SubscriptionManager(models.Manager):
    def create(self, customer, plan, application_fee_percent=None, metadata={},
               quantity=1, trial_end=None, trial_period_days=None,
               **extra_fields):

        if not customer:
            raise ValueError('Subscriptions must have a customer.')
        elif not plan:
            raise ValueError('Subscriptions must have a plan associated.')

        try:
            stripe_sub = get_or_create_stripe_sub(
                subscription_id=None,
                customer=customer.cu_id,
                application_fee_percent=application_fee_percent,
                metadata=metadata,
                plan=plan.plan_id,
                quantity=quantity,
                trial_end=trial_end,
                trial_period_days=trial_period_days
            )
        except stripe.error.InvalidRequestError as e:
            print e
            return None

        sub = self.model(
            sub_id=stripe_sub['id'],
            customer=customer,
            plan=plan,
            status=stripe_sub['status'],
            tax_percent=stripe_sub['tax_percent'],
            trial_period_days=trial_period_days,
            trial_end=stripe_sub['trial_end'],
            trial_start=stripe_sub['trial_start'],
            cancel_at_period_end=stripe_sub['cancel_at_period_end'],
            canceled_at=stripe_sub['canceled_at'],
            current_period_end=stripe_sub['current_period_end'],
            current_period_start=stripe_sub['current_period_start'],
            ended_at=stripe_sub['ended_at'],
            start=stripe_sub['start'],
            **extra_fields)
        sub.save(using=self._db)
        return sub


class ChargeManager(models.Manager):
    def create(self, amount, customer=None, source=None, currency='usd',
               description='', statement_descriptor='', **extra_fields):

        if not amount:
            raise ValueError('Charges must have an amount.')

        try:
            stripe_charge = get_or_create_stripe_charge(
                charge_id=None,
                amount=amount,
                currency=currency,
                description=description,
                receipt_email=customer.user.email if customer else None,
                customer=customer,
                source=source,
                statement_descriptor=statement_descriptor
            )
        except stripe.error.InvalidRequestError as e:
            print e
            return None

        charge = self.model(
            amount=amount,
            customer=customer,
            source=source,
            currency=currency,
            description=description,
            charge_id=stripe_charge['id'],
            amount_refunded=stripe_charge['amount_refunded'],
            paid=stripe_charge['paid'],
            disputed=stripe_charge['disputed'],
            refunded=stripe_charge['refunded'],
            captured=stripe_charge['captured'],
            receipt_sent=stripe_charge['receipt_sent'],
            charge_created=stripe_charge['charge_created'],
            **extra_fields)
        charge.save(using=self._db)
        return charge
