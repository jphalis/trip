from django.db import models
from django.forms import fields
from django_summernote.widgets import SummernoteWidget


class SummernoteTextFormField(fields.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'widget': SummernoteWidget()})
        super(SummernoteTextFormField, self).__init__(*args, **kwargs)


class SummernoteTextField(models.TextField):
    def formfield(self, **kwargs):
        kwargs.update({'form_class': SummernoteTextFormField})
        return super(SummernoteTextField, self).formfield(**kwargs)
