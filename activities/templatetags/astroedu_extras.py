from django import template

from activities.utils import beautify_age_range

register = template.Library()

@register.filter
def beautify_ages(age):
    age_ranges = [obj.name for obj in age.all()]
    return beautify_age_range(age_ranges)
