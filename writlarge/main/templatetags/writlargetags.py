from django import template
from writlarge.main.utils import format_date_range

register = template.Library()


@register.simple_tag
def display_date_range(start, is_ended, ended):
    return format_date_range(start, is_ended, ended)
