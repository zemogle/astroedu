from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Activity, Collection

import logging

class ActivityListView(ListView):
    model = Activity

class CollectionListView(ListView):
    model = Collection
