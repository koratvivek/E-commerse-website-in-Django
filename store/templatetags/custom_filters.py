from django import template
from django.utils.dateformat import format

register = template.Library()

@register.filter
def iso8601(value):
    return value.isoformat()
