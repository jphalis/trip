from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader

from contact.models import Subscription

"""
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string

merge_data = {
    'ORDERNO': "12345", 'TRACKINGNO': "1Z987"
}

plaintext_context = Context(autoescape=False)  # HTML escaping not appropriate in plaintext
subject = render_to_string("message_subject.txt", merge_data, plaintext_context)
text_body = render_to_string("message_body.txt", merge_data, plaintext_context)
html_body = render_to_string("message_body.html", merge_data)

msg = EmailMultiAlternatives(subject=subject, from_email="store@example.com",
                             to=["customer@example.com"], body=text_body)
msg.attach_alternative(html_body, "text/html")
msg.send()
"""


def send_event_email(context):
    """
    Sends an email to mailing list about creation of new event.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    to_emails = ['s4l1818@gmail.com', 'Bobby <mlgyurpi@gmail.com>']  # mailing list
    subject = "TRIP's {0} | {1}".format(context['event_name'],
                                        context['event_start_date'])
    html_content = loader.render_to_string('events/new_event_email.html',
                                           context)
    msg = EmailMultiAlternatives(subject, html_content, 'localpart@sparkpostbox.com', ['jhalis@stevens.edu'], bcc=to_emails)
    msg.attach_alternative(html_content, 'text/html')
    msg.merge_data = {
        's4l1818@gmail.com': {'name': 'Jables'},
        'mlgyurpi@gmail.com': {'name': 'Bobby'}
    }
    msg.esp_extra = {
        'use_sandbox': True  # Only for testing purposes
    }
    msg.send()
