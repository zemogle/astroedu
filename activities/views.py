from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Activity, Collection

import logging

class ActivityListView(ListView):
    model = Activity

class ActivityDetailView(DetailView):
    model = Activity
    slug_field = 'code'
    slug_url_kwarg = 'code'
    view_url_name = 'activities:detail'
    template_name = "activities/activity.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['sections']  = [
                {'code':'goals', 'text':'Goals', 'content':obj.goals,'stream':False},
                {'code':'objectives','text':'Learning Objectives','content': obj.objectives, 'stream':False},
                {'code':'background', 'text':'Background', 'content':obj.background,'stream':True},
                {'code':'fulldesc', 'text':'Full Description', 'content':obj.fulldesc,'stream':True},
                {'code':'evaluation', 'text':'Evaluation', 'content':obj.evaluation,'stream':True},
                {'code':'curriculum', 'text':'Curriculum', 'content':obj.curriculum,'stream':True},
                {'code':'additional_information', 'text':'Additional Information', 'content':obj.additional_information,'stream':True},
                {'code':'conclusion', 'text':'Conclusion', 'content':obj.conclusion,'stream':False},
        ]
        logging.info(context)
        context['page'] = context['object']
        return context

class CollectionDetailView(DetailView):
    model = Collection
    slug_field = 'code'
    slug_url_kwarg = 'code'
    view_url_name = 'activities:detail'
    template_name = "activities/activity_detail.html"

class CollectionListView(ListView):
    model = Collection
