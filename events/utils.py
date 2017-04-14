from django.conf import settings
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.http import HttpResponse
from django.template.loader import render_to_string

from contact.models import Newsletter

"""
from django.template import Context

plaintext_context = Context(autoescape=False)  # HTML escaping not appropriate in plaintext
subject = render_to_string("message_subject.txt", plaintext_context)
text_body = render_to_string("message_body.txt", plaintext_context)
html_body = render_to_string("message_body.html")

msg = EmailMultiAlternatives(subject=subject, from_email="store@example.com",
                             to=["customer@example.com"], body=text_body)
msg.attach_alternative(html_body, "text/html")
msg.send()
"""


def send_event_email(context):
    """
    Sends an email to mailing list about creation of new event.
    """
    email_recipients = Newsletter.objects.subscribed()
    to_emails = []
    merged_data = {}

    if email_recipients.exists():
        # Add users to to_emails and merged_data
        for p in email_recipients:
            context.update({
                'recipient_first_name': p.first_name,
                'recipient_email': p.email
            })
            name = '{0} {1}'.format(p.first_name, p.last_name)
            to_emails.append('{0} <{1}>'.format(name, p.email))
            merged_data.update({p.email: {'name': name}})

        from_email = settings.DEFAULT_FROM_EMAIL
        subject = "TRIP's {0} | {1}".format(context['event_name'],
                                            context['event_start_date'])
        html_content = render_to_string('events/new_event_email.html', context)
        msg = EmailMultiAlternatives(subject, html_content, from_email,
                                     to_emails)
        msg.attach_alternative(html_content, 'text/html')
        msg.merge_data = merged_data  # Hides list from being shown when sent
        # Sandbox from email: 'localpart@sparkpostbox.com'
        # msg.esp_extra = {'use_sandbox': True if settings.DEBUG else False}
        try:
            msg.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
    return False
