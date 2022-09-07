import json
import os
import re
import sys
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
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
from wagtail.images.models import Image
from wagtail.documents.models import Document
from wagtail.users.models import UserProfile
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
        parser.add_argument("-l", "--lang", dest='lang', type=str, help="Import language version")

    def handle(self, *args, **options):
        codes = [lang[0] for lang in settings.LANGUAGES]
        if options['lang'] and options['lang'] in codes:
            lang = options['lang']
        else:
            lang = 'en'
        old_pages = parse_fixture(filename='import_content/smartpages.json')
        pages = join_pages(old_pages, lang=lang)

        self.process_page(pages=pages, lang=lang)


    def process_page(self, pages, lang):
        homepage = HomePage.objects.get(locale__language_code=lang)
        for count,(key, fi) in enumerate(pages.items()):

            if not fi.get('language_code', None) or fi['language_code'] != lang:
                continue
            try:
                newpage  = ContentPage.objects.get(slug = fi['url'].replace("/",""), locale__language_code=lang)
                new = False
                self.stdout.write(f"Updating {fi['url']}")
            except ContentPage.DoesNotExist:
                newpage  = ContentPage(slug = fi['url'].replace("/",""))
                self.stdout.write(f"Creating {fi['url']}")
                new = True
            print(f"{fi['title']}")
            newpage.title = fi['title']
            newpage.content = [('richtext', RichText(markdown.markdown(fi['content'])))]

            if new:
                homepage.add_child(instance=newpage)
                homepage.save()


def parse_fixture(filename):
    with open(filename,'r') as f:
        content = json.load(f)

    return content

def join_pages(old_pages, lang):
    pages = {}
    trans = {}

    for p in old_pages:
        if p['model'] == "smartpages.smartpage":
            pages[p['pk']] = p['fields']
        elif p['model'] == "smartpages.smartpagetranslation":
            if p['fields']["language_code"] == lang:
                trans[p['fields']['master']] = p['fields']
    for k,v in pages.items():
        if trans.get(k):
            pages[k] = {**pages[k], **trans[k]}
    return pages
