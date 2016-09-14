from django.contrib import admin
from django.db import models
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django_summernote.settings import summernote_config

__widget__ = SummernoteWidget if summernote_config['iframe'] \
    else SummernoteInplaceWidget


class SummernoteInlineModelAdmin(admin.options.InlineModelAdmin):
    formfield_overrides = {models.TextField: {'widget': __widget__}}


class SummernoteModelAdmin(admin.ModelAdmin):
    formfield_overrides = {models.TextField: {'widget': __widget__}}
