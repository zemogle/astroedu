import collections
from django.shortcuts import render

from activities.models import Keyword

def index(request):
    keys = set(list(Keyword.objects.all().values_list('tag_id', flat=True)))
    keywords = {}
    for k in keys:
        keywordlist = Keyword.objects.filter(tag_id=k)
        name = keywordlist[0].tag.name
        keywords[name] = keywordlist
    return render(request, 'tagsinspector/index.html', {
        'keywords': collections.OrderedDict(sorted(keywords.items()))
    })
