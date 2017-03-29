from __future__ import unicode_literals

import re
import stripe

from django import forms
from django.conf import settings
from django.utils import timezone

from .models import Charge, Customer
from .utils import get_or_create_stripe_cus  # get_or_create_stripe_charge

# Create your forms here.


class StripeCreditCardForm(forms.Form):
    first_name = forms.CharField(max_length=120, required=False)
    last_name = forms.CharField(max_length=120, required=False)
    email = forms.EmailField(max_length=150, required=False)
    number = forms.CharField(required=False)
    expiry = forms.CharField(max_length=12, required=False)
    cvc = forms.CharField(max_length=5, min_length=3, required=False)
    street_address = forms.CharField(max_length=120, required=False)
    city = forms.CharField(max_length=80, required=False)
    zip_code = forms.CharField(max_length=20, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.customer = kwargs.pop('customer', None)

        super(StripeCreditCardForm, self).__init__(*args, **kwargs)
        self.token = None
        self.amount = None
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY

    def card_luhn_checksum_valid(self):
        """
        Checks to make sure that the card passes a luhn mod-10 checksum.
        """
        number = self.strip_non_numbers(
            self.cleaned_data.get('number', ''))
        sum = 0
        num_digits = len(number)
        oddeven = num_digits & 1
        for count in range(0, num_digits):
            digit = int(number[count])
            if not ((count & 1) ^ oddeven):
                digit = digit * 2
            if digit > 9:
                digit = digit - 9
            sum = sum + digit
        return (sum % 10) == 0

    def strip_non_numbers(self, number):
        """
        Gets rid of all non-numeric characters.
        """
        non_numbers = re.compile('\D')
        return non_numbers.sub('', number)

    def get_or_create_customer(self, email):
        customer = get_or_create_stripe_cus(
            customer_id=self.customer.cu_id if self.customer else None,
            description='Customer for {}'.format(email),
            email=email
        )
        self.customer = customer
        return customer

    def create_card(self, number, expire_month, expire_year, cvc, city,
                    street_address, zip_code, name, email):
        customer = self.get_or_create_customer(email=email)

        try:
            # Create the card for the customer
            self.card = customer.sources.create(source={
                'object': 'card',
                'number': number,
                'exp_month': expire_month,
                'exp_year': expire_year,
                'cvc': cvc,
                'address_city': city,
                'address_line1': street_address,
                'address_zip': zip_code,
                'name': name
            })
            self.token = stripe.Token.create(card={
                "number": number,
                "exp_month": expire_month,
                "exp_year": expire_year,
                "cvc": cvc
            })
        except stripe.error.CardError:
            raise forms.ValidationError(
                "Sorry, we weren't able to validate your credit card "
                "at this time. Please try again later!")

    def charge_customer(self, amount, description, receipt_email):
        # Amount must be a positive integer in cents.
        return Charge.objects.create(
            amount=amount,
            description=description,
            receipt_email=receipt_email.lower(),
            source=self.token
        )

    def clean(self):
        cleaned_data = self.cleaned_data

        # validate card checksum
        if not self.card_luhn_checksum_valid():
            raise forms.ValidationError(
                'The credit card you entered was invalid.')

        today = timezone.now().today()
        this_year = today.year
        this_month = today.month
        expiry = cleaned_data.get('expiry')
        expire_month = int(expiry.replace(' ', '').split('/')[0])
        expire_year = int(expiry.replace(' ', '').split('/')[1])
        city = cleaned_data.get('city')
        street_address = cleaned_data.get('street_address')
        zip_code = cleaned_data.get('zip_code')

        if self.user:
            name = self.user.full_name
            email = self.user.email
        else:
            name = '{} {}'.format(cleaned_data.get('first_name'),
                                  cleaned_data.get('last_name'))
            email = cleaned_data.get('email').lower()

        if expire_year == this_year and expire_month < this_month:
            raise forms.ValidationError(
                'Expiration month must be greater '
                'than or equal to {} for {}'.format(this_month, this_year))

        # Validate card number and create Stripe token
        number = cleaned_data.get('number')
        cvc = cleaned_data.get('cvc')

        if number and cvc:
            # we aren't storing any card ids, so create a new one.
            # When the Stripe "card" object is created, it also functions
            # as the stripe "token".
            self.create_card(number, expire_month, expire_year, cvc, city,
                             street_address, zip_code, name, email)
        return cleaned_data
