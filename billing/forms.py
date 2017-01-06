from __future__ import unicode_literals

import re
import stripe

from django import forms
from django.conf import settings
from django.utils import timezone

# Create your forms here.


class StripeCreditCardForm(forms.Form):
    card_number = forms.CharField(required=False)
    expire_month = forms.IntegerField(min_value=1, max_value=12,
                                      required=False)
    expire_year = forms.IntegerField(min_value=timezone.now().year,
                                     max_value=9999, required=False)
    cvc = forms.CharField(max_length=5, min_length=3, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super(StripeCreditCardForm, self).__init__(*args, **kwargs)
        self.token = None
        self.amount = None
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY

    def card_luhn_checksum_valid(self):
        """
        Checks to make sure that the card passes a luhn mod-10 checksum.
        """
        card_number = self.strip_non_numbers(
            self.cleaned_data.get('card_number', ''))
        sum = 0
        num_digits = len(card_number)
        oddeven = num_digits & 1
        for count in range(0, num_digits):
            digit = int(card_number[count])
            if not ((count & 1) ^ oddeven):
                digit = digit * 2
            if digit > 9:
                digit = digit - 9
            sum = sum + digit
        return (sum % 10) == 0

    def strip_non_numbers(self, card_number):
        """
        Gets rid of all non-numeric characters.
        """
        non_numbers = re.compile('\D')
        return non_numbers.sub('', card_number)

    def get_or_create_customer(self):
        try:
            customer = self.stripe.Customer.retrieve(
                self.user.stripe_customer_id)
        except stripe.error.InvalidRequestError:
            customer = self.stripe.Customer.create(
                description='Customer for {}'.format(self.user.email)
            )

            # persist customer id on user model
            self.user.stripe_customer_id = customer.id
            self.user.save()

        self.customer = customer
        return customer

    def create_card(self, card_number, expire_month, expire_year, cvc):
        customer = self.get_or_create_customer()

        try:
            # Create the card for the customer
            self.card = customer.sources.create(source={
                'object': 'card',
                'number': card_number,
                'exp_month': expire_month,
                'exp_year': expire_year,
                'cvc': cvc,
                'name': self.user.get_full_name()
            })

        except stripe.error.CardError:
            raise forms.ValidationError(
                "Sorry, we weren't able to validate your credit card "
                "at this time. Please try again later!")

    def charge_customer(self, amount, description):
        # Amount must be a positive integer in cents.
        try:
            charge = self.stripe.Charge.create(
                amount=int(amount) * 100,
                currency='usd',
                customer=self.customer.id,
                description=description,
                source=self.card
            )
        except self.stripe.CardError:
            charge = None
        return charge

    def clean(self):
        cleaned_data = self.cleaned_data

        # validate card checksum
        if not self.card_luhn_checksum_valid():
            raise forms.ValidationError(
                'The credit card you entered was invalid.')

        today = timezone.now().today()
        this_year = today.year
        this_month = today.month
        expire_month = int(cleaned_data.get('expire_month'))
        expire_year = int(cleaned_data.get('expire_year'))

        if expire_year == this_year and expire_month < this_month:
            raise forms.ValidationError(
                'Expiration month must be greater '
                'than or equal to {} for {}'.format(this_month, this_year))

        # Validate card number and create Stripe token
        card_number = cleaned_data.get('card_number')
        cvc = cleaned_data.get('cvc')

        if card_number and cvc:
            # we aren't storing any card ids, so create a new one.
            # When the Stripe "card" object is created, it also functions
            # as the stripe "token".
            self.create_card(card_number, expire_month, expire_year, cvc)

        return cleaned_data
