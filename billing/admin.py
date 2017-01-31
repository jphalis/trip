import stripe

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from billing.utils import (get_or_create_stripe_plan, delete_stripe_plan,
                           get_or_create_stripe_cus, delete_stripe_cus,
                           get_or_create_stripe_sub, cancel_stripe_sub,
                           get_or_create_stripe_invoice, delete_stripe_invoice,
                           get_or_create_stripe_charge, convert_tstamp)
from .models import Customer, Plan, Subscription, Invoice, Charge

# Register your models here.

stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_amount', 'is_active',)
    list_filter = ('name', 'created', 'modified', 'is_active',)
    prepopulated_fields = {'plan_id': ['name'], }
    fieldsets = (
        (None,
            {'fields': ('name', 'description', 'plan_id', 'amount', 'currency',
                        'interval',)}),
        ('Optional Information',
            {'fields': ('interval_count', 'statement_descriptor',
                        'trial_period_days',)}),
        ('Permissions',
            {'fields': ('is_active',)}),
        ('Dates',
            {'fields': ('created', 'modified',)})
    )
    readonly_fields = ('created', 'modified',)
    search_fields = ('name', 'plan_id', 'currency',)

    class Meta:
        model = Plan

    def save_model(self, request, obj, form, change):
        plan = get_or_create_stripe_plan(
            plan_id=obj.plan_id,
            name=obj.name,
            amount=obj.amount,
            interval=obj.interval,
            currency=obj.currency,
            interval_count=obj.interval_count,
            statement_descriptor=obj.statement_descriptor,
            trial_period_days=obj.trial_period_days
        )
        if plan:
            obj.plan_id = plan['id']
        obj.save()

    def delete_model(self, request, obj):
        delete_stripe_plan(obj.plan_id)
        obj.delete()


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    list_display_links = ('id', 'user',)
    list_filter = ('created', 'currency',)
    fieldsets = (
        (None,
            {'fields': ('user', 'auto_renew',)}),
        (_('Stripe Information'),
            {'fields': ('cu_id', 'account_balance', 'currency', 'description',
                        'email',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
    )
    readonly_fields = ('cu_id', 'currency', 'email',
                       'created', 'modified',)
    search_fields = ('user__first_name', 'user__last_name', 'email', 'cu_id',)

    class Meta:
        model = Customer

    def save_model(self, request, obj, form, change):
        cu = get_or_create_stripe_cus(
            customer_id=obj.cu_id,
            account_balance=obj.account_balance,
            description=obj.description,
            email=obj.email
        )
        if cu:
            obj.cu_id = cu['id']
        obj.save()

    def delete_model(self, request, obj):
        delete_stripe_cus(obj.cu_id)
        obj.delete()


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'plan_display', 'status_display',)
    list_display_links = ('id', 'customer',)
    list_filter = ('start', 'ended_at', 'canceled_at', 'created', 'modified',)
    fieldsets = (
        (None,
            {'fields': ('sub_id', 'customer', 'plan', 'status', 'quantity',
                        'trial_period_days',)}),
        (_('Dates'),
            {'fields': ('start', 'ended_at', 'current_period_start',
                        'current_period_end', 'trial_start', 'trial_end',
                        'cancel_at_period_end', 'canceled_at',
                        'created', 'modified',)}),
    )
    readonly_fields = ('sub_id', 'customer', 'start', 'created', 'modified',)
    search_fields = ('customer__user__first_name', 'customer__user__last_name',
                     'customer__email', 'plan__plan_id', 'sub_id')

    class Meta:
        model = Subscription

    def save_model(self, request, obj, form, change):
        sub = get_or_create_stripe_sub(
            subscription_id=obj.sub_id,
            customer=obj.customer.cu_id,
            plan=obj.plan.plan_id,
            quantity=obj.quantity,
            trial_end=obj.trial_end,
            trial_period_days=obj.trial_period_days
        )

        if obj.cancel_at_period_end:
            sub = cancel_stripe_sub(subscription_id=obj.sub_id,
                                    at_period_end=True)

        if sub:
            _trial_days = sub['plan']['trial_period_days']
            obj.sub_id = sub['id']
            obj.status = sub['status']
            obj.trial_period_days = _trial_days if _trial_days else 0
            obj.trial_start = convert_tstamp(sub['trial_start'])
            obj.canceled_at = convert_tstamp(sub['canceled_at'])
            obj.current_period_end = convert_tstamp(sub['current_period_end'])
            obj.current_period_start = convert_tstamp(sub['current_period_start'])
            obj.ended_at = convert_tstamp(sub['ended_at'])
            obj.start = convert_tstamp(sub['start'])

        obj.save()

    def delete_model(self, request, obj):
        cancel_stripe_sub(obj.sub_id)
        obj.delete()


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status',)
    list_display_links = ('id', 'customer',)
    list_filter = ('closed', 'paid', 'created', 'modified',)
    fieldsets = (
        (None,
            {'fields': ('customer', 'invoice_id', 'charge', 'subscription',
                        'receipt_number', 'amount_due', 'subtotal', 'total',
                        'currency', 'statement_descriptor', 'description',)}),
        ('Actions',
            {'fields': ('attempted', 'attempted_count', 'closed', 'paid',)}),
        (_('Dates'),
            {'fields': ('period_start', 'period_end',
                        'created', 'modified',)}),
    )
    readonly_fields = ('invoice_id', 'period_start', 'created', 'modified',)
    search_fields = ('customer__user__first_name', 'customer__user__last_name',
                     'customer__user__email', 'receipt_number',)

    class Meta:
        model = Invoice

    def save_model(self, request, obj, form, change):
        invoice = get_or_create_stripe_invoice(
            invoice_id=obj.invoice_id,
            customer_id=obj.customer.cu_id,
            closed=obj.closed,
            description=obj.description,
            forgiven=obj.forgiven,
            statement_descriptor=obj.statement_descriptor,
            subscription=obj.subscription.sub_id
        )

        if invoice:
            obj.invoice_id = invoice['id']
            obj.amount_due = invoice['amount_due']
            obj.attempted = invoice['attempted']
            obj.attempted_count = invoice['attempted_count']
            obj.currency = invoice['currency']
            obj.receipt_number = invoice['receipt_number']
            obj.period_end = convert_tstamp(invoice['period_end'])
            obj.period_start = convert_tstamp(invoice['period_start'])
            obj.subtotal = invoice['subtotal']
            obj.total = invoice['total']
        obj.save()

    def delete_model(self, request, obj):
        delete_stripe_invoice(obj.invoice_id)
        obj.delete()


class ChargeAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'amount', 'charge_created',)
    list_display_links = ('id', 'customer',)
    list_filter = ('paid', 'disputed', 'refunded', 'captured',
                   'charge_created',)
    fieldsets = (
        (None,
            {'fields': ('customer', 'charge_id', 'invoice', 'amount',
                        'amount_refunded', 'currency', 'description',
                        'statement_descriptor',)}),
        ('Actions',
            {'fields': ('paid', 'disputed', 'refunded', 'captured',)}),
        (_('Dates'),
            {'fields': ('charge_created', 'receipt_sent',)}),
    )
    readonly_fields = ('customer', 'charge_id', 'charge_created',
                       'receipt_sent', 'captured', 'refunded', 'disputed',
                       'paid', 'statement_descriptor',)
    search_fields = ('customer__user__first_name', 'customer__user__last_name',
                     'customer__email',)

    class Meta:
        model = Charge

    def save_model(self, request, obj, form, change):
        charge = get_or_create_stripe_charge(
            charge_id=obj.charge_id,
            amount=obj.amount,
            currency=obj.currency,
            description=obj.description,
            customer=obj.customer.cu_id,
            statement_descriptor=obj.statement_descriptor
        )

        if charge:
            obj.charge_id = charge['id']
            obj.amount_refunded = charge['amount_refunded']
            obj.paid = charge['paid']
            obj.disputed = charge['disputed']
            obj.refunded = charge['refunded']
            obj.captured = charge['captured']
            obj.receipt_sent = charge['receipt_sent']
            obj.charge_created = charge['charge_created']
            obj.statement_descriptor = charge['statement_descriptor']
        obj.save()


# admin.site.register(Customer, CustomerAdmin)
admin.site.register(Plan, PlanAdmin)
# admin.site.register(Subscription, SubscriptionAdmin)
# admin.site.register(Invoice, InvoiceAdmin)
# admin.site.register(Charge, ChargeAdmin)
