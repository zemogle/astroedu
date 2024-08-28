import json

from django.conf import settings
from django.core.management.base import BaseCommand

from wagtail_localize.models import TranslatableObject, TranslationSource

from activities.models import *

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Add all activities and other content into wagtail
    """

    help = 'Check through all activities and check for missing pdfs in translation files, and sync to DB if missing'

    def add_arguments(self, parser):
        parser.add_argument("-n", "--name", dest='name', type=str, help="Fix specific meta category by name")
        parser.add_argument("-d", "--diagnostic", dest='diagnostic', action='store_true', help="Show the issue without changing DB")

    def handle(self, *args, **options):
        for model in [Cost, Age, Level, Time, SciCategory, ActivityType, Location, Skills, Learning, Group, Supervised]:
            if options['name']  and options['name'] != str(model.__name__).lower():
                continue
            objs = model.objects.all()

            for o in objs:
                try:
                    transobj = TranslatableObject.objects.get(translation_key=o.translation_key)
                except TranslatableObject.DoesNotExist:
                    logger.error(f'No activity translation for {o.name}')
                    continue
                if options['diagnostic']:
                    print(TranslationSource.objects.filter(object=transobj))
                else:
                    print(TranslationSource.objects.filter(object=transobj).delete())
