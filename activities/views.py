from django.shortcuts import render
from django.views.generic import ListView, DetailView
from wagtail.core.models import Locale

from .models import Activity, Collection

import logging

class ActivityListView(ListView):
    model = Activity

    def get_queryset(self):
        return Activity.objects.filter(locale=Locale.get_active())

class ActivityDetailView(DetailView):
    model = Activity
    template_name = 'activities/activity.html'

    def get_object(self, queryset=None):
        try:
            return Activity.objects.get(locale=Locale.get_active(),code=self.kwargs.get("code"))
        except Activity.DoesNotExist:
            return Activity.objects.get(locale=Locale.get_active(),slug=self.kwargs.get("code"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = context['object']
        return context

class CollectionListView(ListView):
    model = Collection
