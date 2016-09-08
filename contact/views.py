from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page

from .forms import ContactForm

# Create your views here.


# @cache_page(60 * 7)
def inquiry(request):
    form = ContactForm(request.POST or None)
    if form.is_valid() and 'contact_form' in request.POST:
        name = form.cleaned_data['name']
        company = form.cleaned_data['company']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        print message

        subject = 'Trip Inquiry'
        from_email = settings.DEFAULT_HR_EMAIL
        to_email = settings.DEFAULT_HR_EMAIL
        contact_message = "Name: {} | Organization: {} | Email: {} "
        "| Message: {}".format(
            name,
            company,
            email,
            message,
        )
        # send_mail(
        #     subject,
        #     contact_message,
        #     from_email,
        #     [to_email],
        #     fail_silently=True,
        # )
        messages.success(request,
                         "Thank you for your message. "
                         "We have received it, and will be in touch soon!")
        return redirect('home')
    return render(request, 'contact/inquiry.html', {'form': form})
