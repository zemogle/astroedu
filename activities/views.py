from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from wagtail.models import Locale
from wagtail.api.v2.views import BaseAPIViewSet

from .models import Activity, Collection, Organization, AuthorInstitute
from .wagtail_hooks import ActAdmin

activity_modeladmin = ActAdmin()

class OrganizationListView(ListView):
    model = Organization

    def get_queryset(self):
        return Organization.objects.filter(partner_type=1).order_by('name')

class OrganizationDetail(DetailView):
    model = Organization
    template_name = 'activities/organization.html'

    def get_object(self, queryset=None):
        try:
            return Organization.objects.get(slug=self.kwargs.get("slug"))
        except Organization.DoesNotExist:
            raise Http404(f"This partner is not available in {Locale.get_active()}")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity_list = AuthorInstitute.objects.filter(author__orgs=self.object).values_list('activity', flat=True)
        context['people'] = set(AuthorInstitute.objects.filter(author__orgs=self.object).values_list('author__name', flat=True))

        context['activities'] = Activity.objects.filter(locale=Locale.get_active(),id__in=activity_list).order_by('-first_published_at')
        return context

class ActivityListView(ListView):
    model = Activity

    def get_queryset(self):
        return Activity.objects.filter(locale=Locale.get_active()).order_by('-first_published_at')


class CollectionListView(ListView):
    model = Collection

    def get_queryset(self):
        return Collection.objects.filter(locale=Locale.get_active())

class ActivityAPIView(BaseAPIViewSet):
    model = Activity

class ActivityResetDateView(LoginRequiredMixin, DetailView):
    model = Activity

    def get(self, request, *args, **kwargs):
        activity = self.get_object()
        activity.first_published_at = None
        activity.save()
        messages.success(self.request, f'Date reset for {activity.title}')
        return HttpResponseRedirect(activity_modeladmin.url_helper.get_action_url('edit', activity.pk))