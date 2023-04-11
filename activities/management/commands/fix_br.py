from django.conf import settings
from django.core.management.base import BaseCommand
from wagtail.models import Locale
from wagtail.rich_text import RichText

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
        sections = ['goals', 'objectives', 'conclusion', 'short_desc_material', 'further_reading', 'reference']
        streams = ['evaluation', 'materials', 'background', 'fulldesc', 'curriculum', 'additional_information']
        for section in sections:
            cleaned = replace_br(getattr(activity,section))
            setattr(activity, section, cleaned)
        # for stream in streams:
        #     for item in getattr(activity, stream):
        #         cleaned = replace_br(item.value.source)
        activity.save()
        return
    

def replace_br(item):
    soup = BeautifulSoup(item, 'html.parser')
    cleaned_html = soup.decode_contents()

    return cleaned_html
