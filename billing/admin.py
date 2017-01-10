import stripe

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Customer, Plan, Subscription, Invoice, Charge

# Register your models here.

stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'is_active',)
    list_filter = ('name', 'created', 'modified', 'is_active',)
    prepopulated_fields = {'plan_id': ['name'], }
    fieldsets = (
        (None,
            {'fields': ('name', 'plan_id', 'amount', 'currency',
                        'interval',)}),
        ('Optional Information',
            {'fields': ('interval_count', 'metadata', 'statement_descriptor',
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
        try:
            plan = stripe.Plan.retrieve(obj.plan_id)
        except stripe.error.InvalidRequestError:
            plan = None

        if plan:
            plan.amount = int(round(float(obj.amount) * 100))
            plan.metadata = obj.metadata
            plan.name = obj.name
            plan.statement_descriptor = obj.statement_descriptor
            plan.trial_period_days = obj.trial_period_days
            plan.save()
        else:
            stripe.Plan.create(
                id=obj.plan_id,
                amount=int(round(float(obj.amount) * 100)),
                interval=obj.interval,
                interval_count=obj.interval_count,
                metadata=obj.metadata,
                name=obj.name,
                statement_descriptor=obj.statement_descriptor,
                trial_period_days=obj.trial_period_days,
                currency=obj.currency
            )

        obj.save()

    def delete_model(self, request, obj):
        try:
            plan = stripe.Plan.retrieve(obj.plan_id)
        except stripe.error.InvalidRequestError:
            plan = None

        if plan:
            plan.delete()

        obj.delete()


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    list_display_links = ('id', 'user',)
    list_filter = ('created', 'start_date', 'end_date', 'currency',)
    fieldsets = (
        (None,
            {'fields': ('user', 'auto_renew',)}),
        (_('Stripe Information'),
            {'fields': ('cus_id', 'plan_id', 'subscription_id',
                        'account_balance', 'currency',)}),
        (_('Dates'),
            {'fields': ('start_date', 'end_date', 'created', 'modified',)}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
    )
    readonly_fields = ('start_date', 'created', 'modified',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email',
                     'cus_id', 'plan_id', 'subscription_id',)

    class Meta:
        model = Customer

    def save_model(self, request, obj, form, change):
        try:
            cus = stripe.Customer.retrieve(obj.cus_id)
        except stripe.error.InvalidRequestError:
            cus = None

        if cus:
            cus.account_balance = obj.account_balance
            cus.currency = obj.currency
            cus.email = obj.user.email
            cus.save()
        else:
            stripe.Customer.create(
                id=obj.cus_id,
                description='Customer for {}'.format(obj.user.get_full_name),
                account_balance=obj.account_balance,
                currency=obj.currency,
                email=obj.user.email
            )

        obj.save()

    def delete_model(self, request, obj):
        try:
            cus = stripe.Customer.retrieve(obj.cus_id)
        except stripe.error.InvalidRequestError:
            cus = None

        if cus:
            cus.delete()

        obj.delete()


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'plan_display', 'status_display',)
    list_display_links = ('id', 'customer',)
    list_filter = ('start', 'ended_at', 'canceled_at', 'created', 'modified',)
    fieldsets = (
        (None,
            {'fields': ('customer', 'sub_id', 'plan', 'status', 'quantity',
                        'application_fee_percent', 'trial_period_days',)}),
        (_('Dates'),
            {'fields': ('start', 'ended_at', 'current_period_start',
                        'current_period_end', 'trial_start', 'trial_end',
                        'cancel_at_period_end', 'canceled_at',
                        'created', 'modified',)}),
    )
    readonly_fields = ('customer', 'start', 'created', 'modified',)
    search_fields = ('customer__user__first_name', 'customer__user__last_name',
                     'customer__user__email', 'plan_id', 'subscription_id')

    class Meta:
        model = Subscription

    def save_model(self, request, obj, form, change):
        try:
            sub = stripe.Subscription.retrieve(obj.sub_id)
        except stripe.error.InvalidRequestError:
            sub = None

        if sub:
            sub.application_fee_percent = obj.application_fee_percent
            sub.plan['id'] = obj.plan.plan_id
            sub.quantity = obj.quantity
            sub.trial_end = obj.trial_end
            sub.save()
        else:
            stripe.Subscription.create(
                id=obj.sub_id,
                customer=obj.customer.cus_id,
                plan=obj.plan.plan_id,
                application_fee_percent=obj.application_fee_percent,
                quantity=obj.quantity,
                trial_end=obj.trial_end,
                trial_period_days=obj.trial_period_days,
            )

        obj.save()

    def delete_model(self, request, obj):
        try:
            sub = stripe.Subscription.retrieve(obj.sub_id)
        except stripe.error.InvalidRequestError:
            sub = None

        if sub:
            sub.delete()

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
    readonly_fields = ('period_start', 'created', 'modified',)
    search_fields = ('customer__user__first_name', 'customer__user__last_name',
                     'customer__user__email', 'receipt_number',)

    class Meta:
        model = Invoice

    def save_model(self, request, obj, form, change):
        try:
            invoice = stripe.Invoice.retrieve(obj.invoice_id)
        except stripe.error.InvalidRequestError:
            invoice = None

        if invoice:
            invoice.amount_due = obj.amount_due
            invoice.attempted = obj.attempted
            invoice.attempted_count = obj.attempted_count
            invoice.statement_descriptor = obj.statement_descriptor
            invoice.currency = obj.currency
            invoice.closed = obj.closed
            invoice.description = obj.description
            invoice.paid = obj.paid
            invoice.receipt_number = obj.receipt_number
            invoice.period_end = obj.period_end
            invoice.period_start = obj.period_start
            invoice.subtotal = obj.subtotal
            invoice.total = obj.total
            invoice.save()
        else:
            stripe.Invoice.create(customer=obj.customer.cus_id)

        obj.save()

    def delete_model(self, request, obj):
        try:
            invoice = stripe.Invoice.retrieve(obj.invoice_id)
        except stripe.error.InvalidRequestError:
            invoice = None

        if invoice:
            invoice.delete()

        obj.delete()


class ChargeAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'amount', 'charge_created',)
    list_display_links = ('id', 'customer',)
    list_filter = ('paid', 'disputed', 'refunded', 'captured',
                   'charge_created',)
    fieldsets = (
        (None,
            {'fields': ('customer', 'charge_id', 'invoice', 'source', 'amount',
                        'amount_refunded', 'amount_due', 'subtotal', 'total',
                        'currency', 'description', 'statement_descriptor',)}),
        ('Actions',
            {'fields': ('paid', 'disputed', 'refunded', 'captured',)}),
        (_('Dates'),
            {'fields': ('charge_created', 'receipt_sent',)}),
    )
    readonly_fields = ('charge_created', 'receipt_sent',)
    search_fields = ('customer__user__first_name', 'customer__user__last_name',
                     'customer__user__email',)

    class Meta:
        model = Charge

    def save_model(self, request, obj, form, change):
        try:
            charge = stripe.Charge.retrieve(obj.charge_id)
        except stripe.error.InvalidRequestError:
            charge = None

        if charge:
            charge.description = obj.description
            charge.receipt_email = obj.customer.user.email
            charge.save()
        else:
            stripe.Charge.create(
                amount=int(round(float(obj.amount) * 100)),
                currency=obj.currency,
                description=obj.description,
                receipt_email=obj.customer.user.email,
                customer=obj.customer.cus_id,
                statement_descriptor=obj.statement_descriptor
            )

        obj.save()


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Charge, ChargeAdmin)
