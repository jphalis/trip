import stripe

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

# Create your commands here.


class Command(BaseCommand):
    help = 'Creates plans on Stripe account.'

    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        plans = [
            ['Individual', 1000.036],
            ['Corporate Member', 1000],
            ['Future', 1000],
            ['Academic', 1000],
        ]

        for plan in plans:
            stripe.Plan.create(
                amount=int(round(float(plan[1]) * 100)),
                interval='year',
                name=plan[0],
                currency='usd',
                id=slugify(plan[0])
            )
            self.stdout.write(
                self.style.WARNING('Created {} plan.'.format(plan[0])))
        self.stdout.write(
            self.style.SUCCESS('Successfully created all plans on Stripe.'))
