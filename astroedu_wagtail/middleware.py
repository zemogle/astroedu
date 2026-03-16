from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.utils import translation

class DefaultLocaleRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = settings.LANGUAGE_CODE[:2]  # e.g., 'en'
        prefix = f'/{language}/'

        if request.path.startswith(prefix):
            # Strip the language prefix and redirect
            new_path = '/' + request.path[len(prefix):]
            if request.META.get('QUERY_STRING'):
                new_path += '?' + request.META['QUERY_STRING']
            return HttpResponsePermanentRedirect(new_path)

        return self.get_response(request)