from __future__ import unicode_literals

from jsonfield.fields import JSONField

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel
from .managers import CustomerManager, ChargeManager, SubscriptionManager

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
    'statement_descr': ("An arbitrary string to be displayed on your "
                        "customer's credit card statement. This may be "
                        "up to 22 characters."),
    'trial_days': ("Specifies a trial period in (an integer number of) days. "
                   "If you include a trial period, the customer won't be "
                   "billed for the first time until the trial period ends."),
    'status': ("Choices are: trialing, active, past_due, canceled, or unpaid.")
}


@python_2_unicode_compatible
class Plan(TimeStampedModel):
    plan_id = models.SlugField(max_length=255, unique=True, editable=False)
    amount = models.DecimalField(decimal_places=2, max_digits=15,
                                 validators=[MinValueValidator(0.0)],
                                 help_text=HELP_TXT['amount'])
    interval = models.CharField(max_length=5, default='year',
                                help_text=HELP_TXT['interval'])
    name = models.CharField(max_length=150, help_text=HELP_TXT['name'])
    currency = models.CharField(max_length=3, default='usd',
                                help_text=HELP_TXT['currency'])
    interval_count = models.IntegerField(default=1,
                                         help_text=HELP_TXT['interval_count'])
    metadata = JSONField(blank=True, null=True,
                         help_text=HELP_TXT['metadata'])
    statement_descriptor = models.CharField(max_length=22, blank=True,
                                            help_text=HELP_TXT['statement_descr'])
    trial_period_days = models.PositiveIntegerField(default=0, null=True,
                                                    help_text=HELP_TXT['trial_days'])

    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'billing'
        verbose_name = _('plan')
        verbose_name_plural = _('plans')

    def __str__(self):
        return u"{} ({}{})".format(self.name, self.amount, self.currency)


@python_2_unicode_compatible
class Customer(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    cus_id = models.SlugField(max_length=255, unique=True, editable=False)
    plan_id = models.SlugField(max_length=255, blank=True)
    subscription_id = models.SlugField(max_length=120, blank=True)
    account_balance = models.DecimalField(max_digits=9, decimal_places=2,
                                          validators=[MinValueValidator(0.0)])
    currency = models.CharField(max_length=3, default='usd', blank=True,
                                help_text=HELP_TXT['currency'])
    auto_renew = models.BooleanField(default=True)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(help_text=('The default end date will be '
                                               '365 days from now.'))

    is_active = models.BooleanField(default=True)

    objects = CustomerManager()

    class Meta:
        app_label = 'billing'
        verbose_name = _('customer')
        verbose_name_plural = _('customers')

    def __str__(self):
        return str(self.user)

    def update_status(self):
        _user = self.user
        _user.is_active = True if self.end_date >= timezone.now() else False
        _user.save()


@python_2_unicode_compatible
class Subscription(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    sub_id = models.SlugField(max_length=255, unique=True, editable=False)
    application_fee_percent = models.DecimalField(max_digits=3,
                                                  decimal_places=2,
                                                  default=None, null=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    current_period_start = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    start = models.DateTimeField()
    status = models.CharField(max_length=25, help_text=HELP_TXT['status'])
    trial_period_days = models.PositiveIntegerField(default=0, null=True,
                                                    help_text=HELP_TXT['trial_days'])
    trial_end = models.DateTimeField(blank=True, null=True)
    trial_start = models.DateTimeField(blank=True, null=True)

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
class Invoice(TimeStampedModel):
    customer = models.ForeignKey(Customer, related_name="invoices",
                                 on_delete=models.CASCADE)
    invoice_id = models.SlugField(max_length=255, unique=True, editable=False)
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
    receipt_number = models.CharField(max_length=255, blank=True)
    period_end = models.DateTimeField()
    period_start = models.DateTimeField()
    subtotal = models.DecimalField(decimal_places=2, max_digits=9)
    total = models.DecimalField(decimal_places=2, max_digits=9)

    class Meta:
        app_label = 'billing'
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')

    def __str__(self):
        return str(self.customer)

    @property
    def status(self):
        return "Paid" if self.paid else "Open"


@python_2_unicode_compatible
class Charge(models.Model):
    customer = models.ForeignKey(Customer, related_name="charges",
                                 on_delete=models.CASCADE)
    charge_id = models.SlugField(max_length=255, unique=True, editable=False)
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
    statement_descriptor = models.TextField(blank=True)
    charge_created = models.DateTimeField(null=True, blank=True)

    objects = ChargeManager()

    class Meta:
        app_label = 'billing'
        verbose_name = _('charge')
        verbose_name_plural = _('charges')

    def __str__(self):
        return str(self.customer)
