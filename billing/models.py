from __future__ import unicode_literals

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel
from .managers import (PlanManager, CustomerManager, ChargeManager,
                       SubscriptionManager)

# Create your models here.


HELP_TXT = {
    'amount': ("A positive integer in cents (or 0 for a free plan) "
               "representing how much to charge (on a recurring basis)."),
    'currency': ("3-letter ISO code for currency."),
    'interval': ("Specifies billing frequency. Either day, week, month "
                 "or year."),
    'name': ("Name of the plan, to be displayed on invoices and in the web "
             "interface."),
    'interval_count': ("The number of intervals between each subscription "
                       "billing. For example, interval=month and "
                       "interval_count=3 bills every 3 months. Maximum of one "
                       "year interval allowed (1 year, 12 months, or "
                       "52 weeks)."),
    'metadata': ("A set of key/value pairs that you can attach to a plan. "
                 "It can be useful for storing additional information about "
                 "the plan in a structured format."),
    'descriptor': ("An arbitrary string to be displayed on your customer's "
                   "credit card statement. This may be up to 22 characters."),
    'status': ("Choices are: trialing, active, past_due, canceled, or unpaid.")
}


@python_2_unicode_compatible
class Plan(TimeStampedModel):
    plan_id = models.SlugField(max_length=255, unique=True, null=True,
                               blank=True)
    name = models.CharField(max_length=150, help_text=HELP_TXT['name'])
    description = models.TextField()
    amount = models.PositiveIntegerField(help_text=HELP_TXT['amount'])
    interval = models.CharField(max_length=5, default='year',
                                help_text=HELP_TXT['interval'])
    currency = models.CharField(max_length=3, default='usd',
                                help_text=HELP_TXT['currency'])
    interval_count = models.IntegerField(default=1,
                                         help_text=HELP_TXT['interval_count'])
    statement_descriptor = models.CharField(max_length=22, blank=True,
                                            help_text=HELP_TXT['descriptor'])
    trial_period_days = models.PositiveIntegerField(default=0, null=True)

    is_active = models.BooleanField(default=True)

    objects = PlanManager()

    class Meta:
        app_label = 'billing'
        verbose_name = _('plan')
        verbose_name_plural = _('plans')

    def __str__(self):
        return u"{0} ({1}{2})".format(self.name, self.amount, self.currency)

    def display_amount(self):
        return '{} cents'.format(intcomma(self.amount))


@python_2_unicode_compatible
class Customer(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    cu_id = models.SlugField(max_length=255, unique=True, null=True,
                             blank=True)
    account_balance = models.PositiveIntegerField(help_text=HELP_TXT['amount'])
    currency = models.CharField(max_length=3, blank=True)
    description = models.TextField(blank=True)
    email = models.EmailField(max_length=120)
    auto_renew = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    objects = CustomerManager()

    class Meta:
        app_label = 'billing'
        verbose_name = _('customer')
        verbose_name_plural = _('customers')

    def __str__(self):
        return str(self.user)


@python_2_unicode_compatible
class Subscription(TimeStampedModel):
    sub_id = models.SlugField(max_length=255, unique=True, null=True,
                              blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=25)

    trial_period_days = models.PositiveIntegerField(default=0, null=True)
    trial_end = models.DateTimeField(blank=True, null=True)
    trial_start = models.DateTimeField(blank=True, null=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    current_period_start = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)

    objects = SubscriptionManager()

    class Meta:
        app_label = 'billing'
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')

    def __str__(self):
        return str(self.customer)

    @property
    def total_amount(self):
        return self.plan.amount * self.quantity

    def plan_display(self):
        return str(self.plan.name)

    def status_display(self):
        return str(self.status.replace("_", " ").title())


@python_2_unicode_compatible
class Charge(models.Model):
    charge_id = models.SlugField(max_length=255, unique=True, null=True,
                                 blank=True)
    currency = models.CharField(max_length=10, default="usd")
    amount = models.PositiveIntegerField(help_text=HELP_TXT['amount'],
                                         null=True)
    amount_refunded = models.DecimalField(decimal_places=2, max_digits=9,
                                          null=True)
    description = models.TextField(blank=True)
    paid = models.NullBooleanField(null=True)
    disputed = models.NullBooleanField(null=True)
    refunded = models.NullBooleanField(null=True)
    captured = models.NullBooleanField(null=True)
    receipt_sent = models.BooleanField(default=False)
    statement_descriptor = models.TextField(blank=True)
    charge_created = models.DateTimeField(null=True, blank=True)

    objects = ChargeManager()

    class Meta:
        app_label = 'billing'
        verbose_name = _('charge')
        verbose_name_plural = _('charges')

    def __str__(self):
        return str(self.charge_id)
