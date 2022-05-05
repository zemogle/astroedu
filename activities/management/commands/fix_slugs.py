import json
import os
import re
import sys
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.core.management.base import CommandError, BaseCommand
from django.utils.crypto import get_random_string
from io import BytesIO
from wagtail.contrib.redirects.models import Redirect
from wagtail.core.models import Page, Site, Locale
from wagtail.core.rich_text import RichText
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail.users.models import UserProfile

from wagtail_localize.views.submit_translations import TranslationCreator
from wagtail_localize.models import Translation

import markdown
from bs4 import BeautifulSoup

from activities.models import *
from home.models import *

import logging

logger = logging.getLogger(__name__)

published_flag = {'false':False,'true':True}
flag = {'0':False,'1':True}

class Command(BaseCommand):
    """
    Add all activities and other content into wagtail
    """

    help = 'Add all activities and other content into wagtail'

    def add_arguments(self, parser):
        parser.add_argument("-i", "--idcode", dest='code', type=str, help="Import specific activity by code and language version")
        parser.add_argument("-l", "--lang", dest='lang', type=str, help="Import language version")

    def handle(self, *args, **options):
        if options['lang']:
            lang = options['lang']
        else:
            lang = 'en'
        old_pages = parse_fixture(filename='import_content/activities.json')

        activities, trans = join_activites(old_pages, lang)
        for id, values in activities.items():
            if values.get('slug',None):
                try:
                    a = Activity.objects.get(code=values['code'],locale__language_code=lang)
                except Activity.DoesNotExist:
                    print(f"Not found {values['code']}")
                a.slug = values['slug']
                a.save()
                print(f"Saved {a.code}")
            # print(id, values['slug'], values['code'])


def parse_fixture(filename):
    with open(filename,'r') as f:
        content = json.load(f)

    return content

def join_activites(old_pages, lang):
    activities = {}
    trans = {}

    for p in old_pages:
        if p['model'] == "activities.activity":
            activities[p['pk']] = p['fields']
        if p['model'] == "activities.activitytranslation":
            if p['fields']["language_code"] == lang:
                trans[p['fields']['master']] = p['fields']
    for k,v in activities.items():
        if trans.get(k):
            activities[k] = {**activities[k], **trans[k]}
    return activities, trans
