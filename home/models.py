from django.db import models

from wagtail.core.models import Page
from activities.models import Activity


class HomePage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        context['featured'] = Activity.objects.filter(featured=True)
        return context
