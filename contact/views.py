from django.conf import settings
from django.contrib import messages
from django.core.mail import BadHeaderError
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page

from .forms import ContactForm

# Create your views here.


@cache_page(60 * 7)
def inquiry(request):
    form = ContactForm(request.POST or None)
    if form.is_valid() and 'contact_form' in request.POST:
        name = form.cleaned_data['name']
        company = form.cleaned_data['company']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        from_email = settings.DEFAULT_HR_EMAIL
        contact_message = """
            <b>Company:</b> {0}<br><br>
            <b>Name:</b> {1}<br><br>
            <b>Email:</b> {2}<br><br>
            <b>Message:</b> {3}""".format(company, name, email, message)
        email = EmailMessage(
            'TRIP Inquiry',
            contact_message,
            from_email,
            [from_email],
            # ['bcc@example.com'],
            reply_to=[email],
            headers={'From': from_email},
        )
        email.content_subtype = "html"
        try:
            email.send(fail_silently=True)
            messages.success(request,
                             "Thank you for your message. "
                             "We have received it, and will be in touch soon!")
            return redirect('home')
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
    return render(request, 'contact/inquiry.html', {'form': form})
