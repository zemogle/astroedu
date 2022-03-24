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

    # def add_arguments(self, parser):
    #     parser.add_argument("-i", "--idcode", dest='code', type=str, help="Import specific activity by code and language version")
    #     parser.add_argument("-l", "--lang", dest='lang', type=str, help="Import language version")

    def handle(self, *args, **options):

        old_pages = parse_fixture(filename='import_content/activities.json')

        activities = find_images(old_pages)

        for id, values in activities.items():
            if values.get('image', None):
                name = values['image']['file'].split('/')[-1:][0].replace(' ','_')
                image = Image.objects.filter(file__contains=name)
                doc = Document.objects.filter(file__contains=name)
                activities = Activity.objects.filter(code=values['code'], image__isnull=True)
                if image:
                    activities.update(image=image[0])
                    self.stdout.write(f"Updating image for {values['code']} in {activities.values_list('locale', flat=True)}")
                elif doc:
                    docfile = File(file=default_storage.open(doc[0].file.path),name=name)
                    image, c = Image.objects.get_or_create(file=docfile, title=name.rsplit('.',1)[0])
                    activities.update(image=image)
                    self.stdout.write(f"Creating image for {values['code']} in {activities.values_list('locale', flat=True)}")
                else:
                    self.stderr.write(f"No image found for {values['code']} with {name}")


def parse_fixture(filename):
    with open(filename,'r') as f:
        content = json.load(f)

    return content

def find_images(old_pages):
    activities = {}
    titles = {}
    attach = {}
    newactivities = {}
    for p in old_pages:
        if p['model'] == "activities.activity":
            activities[p['pk']] = p['fields']
        elif p['model'] == "activities.activitytranslation":
            if p['fields']["language_code"] == 'en':
                titles[p['fields']['master']] = p['fields']
        elif p['model'] == "activities.attachment":
            if p['fields']["main_visual"]:
                attach[p['fields']['hostmodel']] = p['fields']
    for k,v in activities.items():
        if titles.get(k):
            activities[k]['title'] = titles[k]['title']
        if attach.get(k):
            activities[k]['image'] = attach[k]

    return activities
