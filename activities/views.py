from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from wagtail.models import Locale
from wagtail.api.v2.views import BaseAPIViewSet

from .models import Activity, Collection, Organization, AuthorInstitute

import logging


class OrganizationListView(ListView):
    model = Organization

    def get_queryset(self):
        return Organization.objects.filter(locale=Locale.get_active()).order_by('name')

class OrganizationDetail(DetailView):
    model = Organization
    template_name = 'activities/organization.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity_list = AuthorInstitute.objects.filter(author__org=self.object).values_list('activity', flat=True)
        context['people'] = set(AuthorInstitute.objects.filter(author__org=self.object).values_list('author__name', flat=True))

        context['activities'] = Activity.objects.filter(locale=Locale.get_active(), id__in=activity_list).order_by('-first_published_at')
        return context

class ActivityListView(ListView):
    model = Activity

    def get_queryset(self):
        return Activity.objects.filter(locale=Locale.get_active()).order_by('-first_published_at')


class ActivityDetailView(DetailView):
    model = Activity
    template_name = 'activities/activity.html'

    def get_object(self, queryset=None):
        try:
            return Activity.objects.get(locale=Locale.get_active(),code=self.kwargs.get("code"))
        except Activity.DoesNotExist:
            try:
                return Activity.objects.get(locale=Locale.get_active(),slug=self.kwargs.get("code"))
            except Activity.DoesNotExist:
                activities = Activity.objects.filter(code=self.kwargs.get("code"))
                if activities:
                    return activities[0]
                else:
                    raise Http404(f"This activity is not available in {Locale.get_active()}")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = context['object']
        return context

class CollectionListView(ListView):
    model = Collection

    def get_queryset(self):
        return Collection.objects.filter(locale=Locale.get_active())

class ActivityAPIView(BaseAPIViewSet):
    model = Activity
