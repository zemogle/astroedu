from django.shortcuts import render
from django.views.generic import ListView, DetailView
from wagtail.core.models import Locale

from .models import Activity, Collection

import logging

class ActivityListView(ListView):
    model = Activity

    def get_queryset(self):
        return Activity.objects.filter(locale=Locale.get_active())

class CollectionListView(ListView):
    model = Collection
