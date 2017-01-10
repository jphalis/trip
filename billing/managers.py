from datetime import timedelta

from django.db import models
from django.utils import timezone

from core.utils import rand_code_generator

# Create you managers here.


class CustomerManager(models.Manager):
    def create(self, user, account_balance, plan_id='', subscription_id='',
               currency="usd", cus_id=rand_code_generator(start_text='cus_'),
               end_date=timezone.now() + timedelta(days=365), **extra_fields):

        if not user:
            raise ValueError('Customers must have a user.')

        customer = self.model(user=user, cus_id=cus_id,
                              account_balance=account_balance, plan_id=plan_id,
                              subscription_id=subscription_id,
                              currency=currency, **extra_fields)
        customer.save(using=self._db)
        return customer

    def started_during(self, year, month):
        return self.exclude(
            subscription__status="trialing"
        ).filter(
            subscription__start__year=year,
            subscription__start__month=month
        )

    def active(self):
        return self.filter(
            subscription__status="active"
        )

    def canceled(self):
        return self.filter(
            subscription__status="canceled"
        )

    def canceled_during(self, year, month):
        return self.canceled().filter(
            subscription__canceled_at__year=year,
            subscription__canceled_at__month=month,
        )

    def started_plan_summary_for(self, year, month):
        return self.started_during(year, month).values(
            "subscription__plan"
        ).order_by().annotate(
            count=models.Count("subscription__plan")
        )

    def active_plan_summary(self):
        return self.active().values(
            "subscription__plan"
        ).order_by().annotate(
            count=models.Count("subscription__plan")
        )

    def canceled_plan_summary_for(self, year, month):
        return self.canceled_during(year, month).values(
            "subscription__plan"
        ).order_by().annotate(
            count=models.Count("subscription__plan")
        )


class SubscriptionManager(models.Manager):
    def create(self, customer, plan, start, current_period_start,
               status='active', sub_id=rand_code_generator(start_text='sub_'),
               **extra_fields):

        if not customer:
            raise ValueError('Subscriptions must have a customer.')
        elif not plan:
            raise ValueError('Subscriptions must have a plan associated.')
        elif not start:
            raise ValueError('Subscriptions must have a start date.')
        elif not current_period_start:
            raise ValueError('Subscriptions must have a start date.')
        elif not status:
            raise ValueError('Subscriptions must have a status.')

        sub = self.model(customer=customer, plan=plan, start=start,
                         status=status, sub_id=sub_id,
                         current_period_start=current_period_start,
                         **extra_fields)
        sub.save(using=self._db)
        return sub


class ChargeManager(models.Manager):
    def create(self, customer, source, amount, currency='usd', description='',
               charge_id=rand_code_generator(start_text='charge_'),
               **extra_fields):

        if not customer:
            raise ValueError('Charges must have a customer.')
        elif not source:
            raise ValueError('Charges must have a source.')
        elif not amount:
            raise ValueError('Charges must have an amount.')

        charge = self.model(customer=customer, source=source, amount=amount,
                            currency=currency, description=description,
                            charge_id=charge_id, **extra_fields)
        charge.save(using=self._db)
        return charge

    def during(self, year, month):
        return self.filter(
            charge_created__year=year,
            charge_created__month=month
        )

    def paid_totals_for(self, year, month):
        return self.during(year, month).filter(
            paid=True
        ).aggregate(
            total_amount=models.Sum("amount"),
            total_refunded=models.Sum("amount_refunded")
        )
