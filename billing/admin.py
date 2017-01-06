from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Customer, Plan, Subscription, Invoice, Charge

# Register your models here.


class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'is_active',)
    list_filter = ('name', 'created', 'modified', 'is_active',)
    fieldsets = (
        (None,
            {'fields': ('name', 'amount', 'currency', 'interval',
                        'plan_id',)}),
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


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    list_display_links = ('id', 'user',)
    list_filter = ('created', 'start_date', 'end_date', 'currency',)
    fieldsets = (
        (None,
            {'fields': ('user', 'auto_renew',)}),
        (_('Stripe Information'),
            {'fields': ('plan_id', 'subscription_id', 'account_balance',
                        'currency',)}),
        (_('Dates'),
            {'fields': ('start_date', 'end_date', 'created', 'modified',)}),
    )
    readonly_fields = ('start_date', 'created', 'modified',)
    search_fields = ('user__first_name', 'user_last_name', 'user__email',
                     'plan_id', 'subscription_id')

    class Meta:
        model = Customer


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan_display', 'status_display',)
    list_display_links = ('id', 'user',)
    list_filter = ('start', 'ended_at', 'canceled_at', 'created', 'modified',)
    fieldsets = (
        (None,
            {'fields': ('user', 'plan', 'status', 'quantity',
                        'application_fee_percent',)}),
        (_('Dates'),
            {'fields': ('start', 'ended_at', 'current_period_start',
                        'current_period_end', 'trial_start', 'trial_end',
                        'cancel_at_period_end', 'canceled_at',
                        'created', 'modified',)}),
    )
    readonly_fields = ('start_date', 'created', 'modified',)
    search_fields = ('user__first_name', 'user_last_name', 'user__email',
                     'plan_id', 'subscription_id')

    class Meta:
        model = Subscription


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'closed', 'paid',)
    list_display_links = ('id', 'user',)
    list_filter = ('closed', 'paid', 'created', 'modified',)
    fieldsets = (
        (None,
            {'fields': ('user', 'charge', 'subscription', 'receipt_number',
                        'amount_due', 'subtotal', 'total', 'currency',
                        'statement_descriptor', 'description',)}),
        ('Actions',
            {'fields': ('attempted', 'attempted_count', 'closed', 'paid',)}),
        (_('Dates'),
            {'fields': ('period_start', 'period_end',
                        'created', 'modified',)}),
    )
    readonly_fields = ('period_start', 'attempted_count', 'receipt_number',
                       'created', 'modified',)
    search_fields = ('user__first_name', 'user_last_name', 'user__email',
                     'receipt_number',)

    class Meta:
        model = Invoice


class ChargeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'charge_created',)
    list_display_links = ('id', 'user',)
    list_filter = ('paid', 'disputed', 'refunded', 'captured',
                   'charge_created',)
    fieldsets = (
        (None,
            {'fields': ('user', 'invoice', 'source', 'amount',
                        'amount_refunded', 'currency',
                        'amount_due', 'subtotal', 'total', 'currency',
                        'description',)}),
        ('Actions',
            {'fields': ('paid', 'disputed', 'refunded', 'captured',)}),
        (_('Dates'),
            {'fields': ('charge_created', 'receipt_sent', 'modified',)}),
    )
    readonly_fields = ('charge_created', 'receipt_sent', 'modified',)
    search_fields = ('user__first_name', 'user_last_name', 'user__email',)

    class Meta:
        model = Charge


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Charge, ChargeAdmin)
