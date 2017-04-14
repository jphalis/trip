from django import template


register = template.Library()


@register.filter(name="divide")
def divide(value, arg):
    return "{0:.2f}".format((int(value) / int(arg)) if int(arg) != 0 else 0)
