import json
import os
import re


from django.conf import settings

from django.core.management.base import CommandError, BaseCommand

from wagtail.core.models import Locale


from activities.models import *

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Add all activities and other content into wagtail
    """

    help = 'Add all activities and other content into wagtail'

    def add_arguments(self, parser):
        parser.add_argument("-c", "--code", dest='code', type=str, help="Fix specific activity by code and language version")

    def handle(self, *args, **options):
        en = Locale.objects.get(language_code='en')
        it = Locale.objects.get(language_code='it')
        if options['code']:
            activities = Activity.objects.filter(code=options['code'], locale=en)
        else:
            activities = Activity.objects.filter(locale=en)

        for a in activities:
            try:
                a_it = Activity.objects.get(locale=it,code=a.code)
            except Activity.DoesNotExist:
                logger.error(f'No activity {a.code}')
                continue
            a_it.first_published_at = a.first_published_at
            a_it.save()
            logger.info(f'Updated {a_it.code}')
