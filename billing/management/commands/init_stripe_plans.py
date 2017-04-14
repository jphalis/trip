import stripe

from django.conf import settings
from django.core.management.base import BaseCommand

from billing.models import Plan

# Create your commands here.


class Command(BaseCommand):
    help = 'Creates plans on Stripe account.'

    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        plans = [
            [
                'Individual',
                15000,
                "Any person interested in the promotion and development of "
                "the professional liability industry is eligible for "
                "membership<br/><br/><br/><br/>"
            ],
            [
                'Corporate Member',
                100000,
                "Must be an employee of a Corporate Sponsor\n\n"
                "Corporate affiliates hold the same rights as an individual "
                "member"
            ],
            [
                'Future',
                5000,
                "Must be 35 years of age or younger and involved in the "
                "professional liability industry\n\n"
                "Full membership benefits, including member discounts for "
                "event registration"
            ],
            [
                'Academic',
                0,
                "Website access only\n\n"
                "Must be a student or teacher at an academic institution"
            ],
            [
                'Admin',
                0,
                "Used for administrative purposes only"
            ]
        ]

        for plan in plans:

            if not Plan.objects.filter(name=plan[0]).exists():
                new_p = Plan.objects.create(
                    name=plan[0],
                    amount=plan[1],
                    interval='year',
                    description=plan[2] if plan[2] else ''
                )

                if plan[0] == 'Admin':
                    new_p.is_active = False
                    new_p.save(update_fields=['is_active'])

                self.stdout.write(
                    self.style.WARNING('Created {} plan.'.format(new_p.name))
                )
        self.stdout.write(
            self.style.SUCCESS('Successfully created all plans on Stripe.'))
