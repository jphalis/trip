from __future__ import unicode_literals

import stripe

from datetime import timedelta
from jsonfield.fields import JSONField

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel
from .managers import CustomerManager, ChargeManager
from .signals import membership_dates_update

# Create your models here.


NOW = timezone.now()

HELP_TEXT = {
    'amount': ('A positive integer in cents (or 0 for a free plan) '
               'representing how much to charge (on a recurring basis).'),
    'currency': ('3-letter ISO code for currency.'),
    'interval': ('Specifies billing frequency. Either day, week, month '
                 'or year.'),
    'name': ('Name of the plan, to be displayed on invoices and in the web '
             'interface.'),
    'interval_count': ('The number of intervals between each subscription '
                       'billing. For example, interval=month and '
                       'interval_count=3 bills every 3 months. Maximum of one '
                       'year interval allowed (1 year, 12 months, or '
                       '52 weeks).'),
    'metadata': ('A set of key/value pairs that you can attach to a plan. '
                 'It can be useful for storing additional information about '
                 'the plan in a structured format.'),
    'statement_descriptor': ('An arbitrary string to be displayed on your '
                             'customer’s credit card statement. This may be '
                             'up to 22 characters.'),
    'trial_period_days': ('Specifies a trial period in (an integer number of) '
                          'days. If you include a trial period, the customer '
                          'won’t be billed for the first time until the trial '
                          'period ends.'),
    'status': ('Choices are: trialing, active, past_due, canceled, or unpaid')
}


class StripeObject(TimeStampedModel):
    stripe_id = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Plan(StripeObject):
    amount = models.DecimalField(decimal_places=2, max_digits=15,
                                 validators=[MinValueValidator(0.0)],
                                 help_text=HELP_TEXT['amount'])
    interval = models.CharField(max_length=5, help_text=HELP_TEXT['interval'])
    name = models.CharField(max_length=150, help_text=HELP_TEXT['name'])
    currency = models.CharField(max_length=3, default="usd",
                                help_text=HELP_TEXT['currency'])
    plan_id = models.CharField(max_length=255, unique=True)
    interval_count = models.IntegerField(default=1,
                                         help_text=HELP_TEXT['interval_count'])
    metadata = JSONField(null=True, help_text=HELP_TEXT['metadata'])
    statement_descriptor = models.CharField(max_length=22, blank=True,
                                            help_text=HELP_TEXT['statement_descriptor'])
    trial_period_days = models.IntegerField(null=True,
                                            validators=[MinValueValidator(0)],
                                            help_text=HELP_TEXT['trial_period_days'])

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return u"{} ({}{})".format(self.name, self.amount, self.currency,)


@python_2_unicode_compatible
class Customer(StripeObject):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    plan_id = models.CharField(max_length=120, blank=True)
    subscription_id = models.CharField(max_length=120, blank=True)
    account_balance = models.DecimalField(max_digits=9, decimal_places=2,
                                          validators=[MinValueValidator(0.0)])
    currency = models.CharField(max_length=3, default="usd", blank=True)
    auto_renew = models.BooleanField(default=True)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(default=NOW + timedelta(days=365))

    objects = CustomerManager()

    class Meta:
        app_label = 'billing'
        verbose_name = _('customer')
        verbose_name_plural = _('customers')

    def __str__(self):
        return str(self.user)

    @property
    def stripe_customer(self):
        return stripe.Customer.retrieve(self.stripe_id)

    def update_status(self):
        self.user.is_active = True if self.end_date >= NOW else False
        self.user.save()


def update_membership_status(sender, instance, created, **kwargs):
    if not created:
        instance.update_status()


post_save.connect(update_membership_status, sender=Customer)


def update_membership_dates(sender, new_start_date, **kwargs):
    customer = sender
    current_end_date = customer.end_date

    if current_end_date >= new_start_date:
        # append new_start date plus offset to date end of the instance
        customer.end_date = current_end_date + timedelta(days=365)
    else:
        # set a new start date and new end date with the same offset.
        customer.start_date = new_start_date
        customer.end_date = new_start_date + timedelta(days=365)

    customer.save()


membership_dates_update.connect(update_membership_dates)


class Subscription(StripeObject):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    application_fee_percent = models.DecimalField(max_digits=3,
                                                  decimal_places=2,
                                                  default=None, null=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    current_period_start = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    start = models.DateTimeField()
    status = models.CharField(max_length=25, help_text=HELP_TEXT['status'])
    trial_end = models.DateTimeField(blank=True, null=True)
    trial_start = models.DateTimeField(blank=True, null=True)

    @property
    def stripe_subscription(self):
        return stripe.Customer.retrieve(
            self.user.stripe_id).subscriptions.retrieve(self.stripe_id)

    @property
    def total_amount(self):
        return self.plan.amount * self.quantity

    def plan_display(self):
        return str(self.plan.name)

    def status_display(self):
        return str(self.status.replace("_", " ").title())

    def delete(self, using=None):
        """
        Set values to None while deleting the object so that any
        lingering references will not show previous values.
        """
        super(Subscription, self).delete(using=using)
        self.status = None
        self.quantity = 0
        self.amount = 0


class Invoice(StripeObject):
    user = models.ForeignKey(Customer, related_name="invoices",
                                 on_delete=models.CASCADE)
    amount_due = models.DecimalField(decimal_places=2, max_digits=9)
    attempted = models.NullBooleanField()
    attempt_count = models.PositiveIntegerField(null=True)
    charge = models.ForeignKey("Charge", null=True, related_name="invoices",
                               on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, null=True,
                                     on_delete=models.CASCADE)
    statement_descriptor = models.TextField(blank=True)
    currency = models.CharField(max_length=10, default="usd")
    closed = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    paid = models.BooleanField(default=False)
    receipt_number = models.TextField(blank=True)
    period_end = models.DateTimeField()
    period_start = models.DateTimeField()
    subtotal = models.DecimalField(decimal_places=2, max_digits=9)
    total = models.DecimalField(decimal_places=2, max_digits=9)

    @property
    def status(self):
        return "Paid" if self.paid else "Open"

    @property
    def stripe_invoice(self):
        return stripe.Invoice.retrieve(self.stripe_id)


class Charge(StripeObject):
    user = models.ForeignKey(Customer, related_name="charges",
                             on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, null=True, related_name="charges",
                                on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    currency = models.CharField(max_length=10, default="usd")
    amount = models.DecimalField(decimal_places=2, max_digits=9, null=True)
    amount_refunded = models.DecimalField(decimal_places=2, max_digits=9,
                                          null=True)
    description = models.TextField(blank=True)
    paid = models.NullBooleanField(null=True)
    disputed = models.NullBooleanField(null=True)
    refunded = models.NullBooleanField(null=True)
    captured = models.NullBooleanField(null=True)
    receipt_sent = models.BooleanField(default=False)
    charge_created = models.DateTimeField(null=True, blank=True)

    objects = ChargeManager()

    @property
    def stripe_charge(self):
        return stripe.Charge.retrieve(self.stripe_id)
