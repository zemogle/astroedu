from django.db import models

from wagtail.core.models import Page, Locale
from activities.models import Activity


class HomePage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        context['featured'] = Activity.objects.filter(featured=True, locale=Locale.get_active())
        return context
