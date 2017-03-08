from django.test import TestCase
from django.utils import timezone

from accounts.models import MyUser
from ..forms import StripeCreditCardForm


class StripeCreditCardFormUnitTest(TestCase):

    def setUp(self):
        self.user = MyUser.objects.create_user(
            email='test@user.com', first_name='John', last_name='Doe',
            password='pbkdf2_sha256$12000$64NIBRztT1eL$ip9P9F2vYdCvIXM')

    def test_strip_non_numeric_characters(self):
        value = '1111-1111-1111-1111'
        expected_result = value.replace('-', '')
        form = StripeCreditCardForm(user=self.user)
        actual_result = form.strip_non_numbers(value)
        self.assertEqual(expected_result, actual_result,
                         'Expected result: {} did not match actual '
                         'result: {}'.format(expected_result, actual_result))

    def test_luhn_checksum(self):
        card_data = {
            'expire_month': '12',
            'expire_year': str(timezone.now().year + 1),
            'cvc': '111'
        }

        # bad credit card number
        card_data['card_number'] = '0123-4567-9089-0000'
        form1 = StripeCreditCardForm(user=self.user, data=card_data)
        # call .is_valid() to populate cleaned data
        form1.is_valid()
        self.assertFalse(form1.card_luhn_checksum_valid(),
                         'Card number should not be valid.')

        # good credit card number
        card_data['card_number'] = '4242-4242-4242-4242'
        form2 = StripeCreditCardForm(user=self.user, data=card_data)
        form2.is_valid()
        self.assertTrue(form2.card_luhn_checksum_valid(),
                        'Card number should be valid.')
