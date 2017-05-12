import stripe

from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.models import MyUser
from billing.models import Customer, Plan, Subscription
from events.models import Event

# Create your commands here.


class Command(BaseCommand):
    help = """Creates plans on Stripe account, creates demo accounts,
    and creates sample events."""

    def handle(self, *args, **options):
        _create_stripe_plans(self)
        _create_demo_accounts(self)
        _create_events(self)
        self.stdout.write(self.style.SUCCESS('Successfully created demo data.'))


def _create_stripe_plans(command):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    plans = [
        ['Individual', 15000, "Any person interested in the promotion and "
                              "development of the professional liability "
                              "industry is eligible for membership"
                              "<br/><br/><br/><br/>"],
        ['Corporate Member', 100000, "Must be an employee of a Corporate "
                                     "Sponsor\n\nCorporate affiliates hold "
                                     "the same rights as an individual "
                                     "member"],
        ['Future', 5000, "Must be 35 years of age or younger and involved in "
                         "the professional liability industry\n\nFull "
                         "membership benefits, including member discounts for "
                         "event registration"],
        ['Academic', 0, "Website access only\n\nMust be a student or teacher "
                        "at an academic institution"],
        ['Admin', 0, "Used for administrative purposes only"]
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
            command.stdout.write(
                command.style.WARNING('Created {} plan.'.format(new_p.name))
            )
    command.stdout.write(
        command.style.SUCCESS('Successfully created all plans on Stripe.'))
    return True


def _create_demo_accounts(command):
    if not MyUser.objects.filter(email__iexact='user@demo.com').exists():
        user = MyUser.objects.create_user(
            email='user@demo.com', first_name='Demo', last_name='User',
            password='demo'
        )
        cu = Customer.objects.create(user=user, account_balance=0)
        plan = Plan.objects.get(name='Individual')
        sub = Subscription.objects.create(customer=cu, plan=plan)
        command.stdout.write(command.style.WARNING('Created demo user account.'))
    if not MyUser.objects.filter(email__iexact='admin@demo.com').exists():
        MyUser.objects.create_superuser(
            email='admin@demo.com', first_name='Admin', last_name='Account',
            password='demo')
        command.stdout.write(command.style.WARNING('Created demo admin account.'))
    command.stdout.write(command.style.SUCCESS('Successfully created accounts.'))
    return True


def _create_events(command):
    import random
    from datetime import date, timedelta

    firstJan = date.today().replace(day=1, month=1)
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In "
    "tempus adipiscing felis, sit amet blandit ipsum volutpat sed. Morbi "
    "porttitor, eget accumsan dictum, nisi libero ultricies ipsum, in posuere "
    "mauris neque at erat."
    events = [
        ["E3 Convention", 0, 10000, text],
        ["TED Talk", 1000, 30000, text],
        ["Stevens Graduation", 0, 10000, text],
        ["Mark Cuban's Speech", 5000, 50000, text],
        ["Kirk Sanderson's Birthday", 10000, 100000, text]
    ]
    for event in events:
        if not Event.objects.filter(name=event[0]).exists():
            start_date = firstJan + timedelta(days=random.randint(0, 365))
            new_event = Event.objects.create(name=event[0],
                                             start_date=start_date,
                                             end_date=start_date + timedelta(days=3),
                                             member_fee=event[1],
                                             non_member_fee=event[2],
                                             email_description=event[3],
                                             description=event[3])
            command.stdout.write(
                command.style.WARNING('Created {} event.'.format(new_event.name))
            )
    command.stdout.write(command.style.SUCCESS('Successfully created events.'))
    return True
