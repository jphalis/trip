from decimal import Decimal

from django.db import models

# Create you managers here.


class CustomerManager(models.Manager):
    def create(self, user, billing_fee, **extra_fields):
        """
        Creates a customer.
        """
        if not user:
            raise ValueError('Customers must have a user.')
        elif not billing_fee:
            raise ValueError('Customers must have a billing fee.')

        customer = self.model(user=user, billing_fee=Decimal(str(billing_fee)),
                              **extra_fields)
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


class ChargeManager(models.Manager):
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
