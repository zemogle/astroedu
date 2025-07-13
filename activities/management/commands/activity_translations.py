import json

from django.conf import settings
from django.core.management.base import BaseCommand
from wagtail.models import Locale

from activities.models import *

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Add all activities and other content into wagtail
    """

    help = 'Check through all activities and check for missing pdfs in translation files, and sync to DB if missing'

    def add_arguments(self, parser):
        parser.add_argument("-c", "--code", dest='code', type=str, help="Fix specific activity by code")
        parser.add_argument("-a", "--all", dest='all', action='store_true', help="Fix all activities")
        parser.add_argument("-d", "--diagnostic", dest='diagnostic', action='store_true', help="Show the issue without changing DB")

    def handle(self, *args, **options):
        en = Locale.objects.get(language_code='en')
        if options['code']:
            activities = Activity.objects.filter(code=options['code'], locale=en)
        elif options['all']:
            activities = Activity.objects.filter(locale=en)
        else:
            logger.error('Select either --code or --all to run this command.')
            return