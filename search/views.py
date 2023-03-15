from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse

from activities.models import Activity
from wagtail.search.models import Query
from wagtail.models import Page, Locale
from wagtail.search.backends import get_search_backend

import logging

def search(request):
    search_query = request.GET.get('q', None)
    page = request.GET.get('page', 1)

    # Search
    if search_query:
        s = get_search_backend()
        search_results = s.search(search_query, Activity.objects.live().filter(locale=Locale.get_active()))
        logging.error('here')
    else:
        search_results = Activity.objects.live()

    # # Pagination
    # paginator = Paginator(search_results, 10)
    # try:
    #     search_results = paginator.page(page)
    # except PageNotAnInteger:
    #     search_results = paginator.page(1)
    # except EmptyPage:
    #     search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
    })
