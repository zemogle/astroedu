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

    # def add_arguments(self, parser):
    #     parser.add_argument("-i", "--idcode", dest='code', type=str, help="Import specific activity by code and language version")
    #     parser.add_argument("-l", "--lang", dest='lang', type=str, help="Import language version")

    def handle(self, *args, **options):

        it= Locale.objects.get(language_code='it')
        activities = Activity.objects.filter(locale__language_code='en')

        for activity in activities:
            if activity.has_translation(locale=it) and activity.image:
                activity_it = Activity.objects.get(locale=it, code=activity.code)
                activity_it.image=activity.image
                activity_it.save()
                self.stdout.write(f"Updating image for {activity_it.code}")
            else:
                self.stderr.write(f"No image found for {activity_it.code}")
