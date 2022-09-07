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
from wagtail.models import Page, Site, Locale
from wagtail.rich_text import RichText
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
        codes = [lang[0] for lang in settings.LANGUAGES]
        if options['lang'] and options['lang'] in codes:
            code = options['lang']
        else:
            code = 'en'


        l, c = Locale.objects.get_or_create(language_code=code)
        if options['code']:
            activities = Activity.objects.filter(locale=l, code=options['code'])
        else:
            activities = Activity.objects.filter(locale=l)
        for activity in activities:
            self.process_meta(activity=activity, locale=l)

    def process_meta(self, activity, locale):
        group = {
                'level':Level,
                'learning':Learning,
                }
        # Level fix
        for name, obj in group.items():
            for item in getattr(activity,name).all():
                newitem = obj.objects.get(translation_key=item.translation_key, locale=locale)
                getattr(activity,name).remove(item)
                getattr(activity,name).add(newitem)
                self.stdout.write(f'{activity.title}: Replace {item.name} with {newitem.name}')
                activity.save()
        return
