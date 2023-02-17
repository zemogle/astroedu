# -*- coding: utf-8 -*-
import os
import re
import urllib
import logging
import time
import importlib

from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail, BadHeaderError
from django.conf import settings
from django.core.management.base import BaseCommand

# Get an instance of a logger
logger = logging.getLogger('astroEDU')


def get_python_thing(fullname):
    module_name, thing_name = fullname.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, thing_name)


def generate_one(objdef, obj, file_type, force=False, site_url=None):
    ctx = {'slug': obj.slug, 'code': obj.code, 'ext': file_type}
    if hasattr(obj, 'language_code'):
        ctx['lang'] = obj.language_code
    filename = objdef['filename_tpl'] % ctx
    path = os.path.join(settings.MEDIA_ROOT, objdef['path'], filename)
    if force or (not (os.path.exists(path) and os.path.getmtime(path) > time.mktime(obj.modification_date.timetuple()))):
        if not site_url:
            site_url = settings.SITE_URL
        renderer = get_python_thing(objdef['renderers'][file_type])
        renderer(obj, path, site_url=site_url)
    return filename


def get_generated_url(objdef, file_type, code, lang=None):
    model = get_python_thing(objdef['model'])
    if lang:
        obj = model.objects.available().language(lang).get(code=code)
    else:
        obj = model.objects.available().get(code=code)
    filename = generate_one(objdef, obj, file_type)
    return settings.MEDIA_URL + objdef['path'] + filename

def beautify_age_range(age_ranges):
    'Unifies a list of age ranges into a string. Input list must be sorted.'
    age_min = ''
    age_max = ''
    error = False

    # Sort age ranges
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    age_ranges = sorted(age_ranges, key=alphanum_key)

    for item in age_ranges:
        if ' - ' in item:
            x, y = item.split(' - ')
            if not age_min and not age_max:  # first range
                age_min = x
                age_max = x
            elif not age_max:  # the previous range was n+, that should have been the last
                error = True
            if x == age_max:  # checking the list is sorted; previous range max = this range min
                age_max = y
            else:
                error = True
        elif '+' in item:
            x = item[:item.find('+')]
            if x == age_max:  # checking the list is sorted; previous range max = this range min
                age_max = ''
            else:
                error = True
            break

    if error:
        return ' '.join(age_ranges)
    elif age_max:
        return age_min + ' - ' + age_max
    elif age_min:
        return age_min + '+'
    else:
        return ' '.join(age_ranges)


class UnsupportedMediaPathException(Exception):
    pass


def local_resource(uri):
    """
    Returns the full file path and a relative path for the resource
    """
    # because activities.utils.UnsupportedMediaPathException: media urls must start with /media/ or /static/
    if uri.startswith(settings.SITE_URL):
        uri = uri.replace(settings.SITE_URL, '')
    if uri.startswith(settings.MEDIA_URL):
        local = uri.replace(settings.MEDIA_URL, '')
        path = os.path.join(settings.MEDIA_ROOT, local)
    elif uri.startswith(settings.STATIC_URL):
        local = uri.replace(settings.STATIC_URL, '')
        path = os.path.join(settings.STATIC_ROOT, local)
    else:
        raise UnsupportedMediaPathException('media urls must start with %s or %s' % (settings.MEDIA_URL, settings.STATIC_URL))

    # return path
    return urllib.parse.unquote(path), urllib.parse.unquote(local)


# def send_notification_mail():
#     # import logging
#     # logger = logging.getLogger(__name__)
#
#     from_email = settings.DEFAULT_FROM_EMAIL
#     to = 'rinoo7@gmail.com'
#
#     subject = 'test email'
#     html_body = '<b>test</b> email'
#     text_body = strip_tags( html_body )
#
#     # Send
#
#     if subject and html_body and from_email and to:
#         #logger.info(settings.EMAIL_HOST)
#         msg = EmailMultiAlternatives( subject, text_body, from_email, [to] )
#         msg.attach_alternative( html_body, 'text/html' )
#         msg.send()
#
#     return



def get_qualified_url(local_url):
    # current_site = Site.objects.get_current()
    current_site = 'astroedu.iau.org'
    return 'http://%s%s' % (current_site, local_url)
