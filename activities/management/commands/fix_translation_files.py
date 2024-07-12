import json

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel
from wagtail.models import Locale
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

        for a in activities:
            try:
                transobj = TranslatableObject.objects.get(translation_key=a.translation_key)
            except TranslatableObject.DoesNotExist:
                logger.error(f'No activity translation for {a.code}')
                continue
            try:
                ts = TranslationSource.objects.get(object=transobj)
            except:
                logger.error(f'Error with {a.code}')
                continue
            data = json.loads(ts.content_json)

            pk_field = Activity._meta.pk
            kwargs = {}

            # If model is a child via multitable inheritance, we need to set ptr_id fields all the way up
            # to the main PK field, as Django won't populate these for us automatically.
            while pk_field.remote_field and pk_field.remote_field.parent_link:
                kwargs[pk_field.attname] = data['pk']
                pk_field = pk_field.remote_field.model._meta.pk

            kwargs[pk_field.attname] = data['pk']
            for field_name, field_value in data.items():
                try:
                    field = Activity._meta.get_field(field_name)
                except FieldDoesNotExist:
                    continue

                # Filter out reverse relations
                if isinstance(field, ForeignObjectRel):
                    continue

                if field.remote_field and isinstance(field.remote_field, models.ManyToManyRel):
                    related_objects = field.remote_field.model._default_manager.filter(pk__in=field_value)
                    kwargs[field.attname] = list(related_objects)

                elif field.remote_field and isinstance(field.remote_field, models.ManyToOneRel):
                    if field_value is None:
                        kwargs[field.attname] = None
                    else:
                        try:
                            clean_value = field.remote_field.model._meta.get_field(field.remote_field.field_name).to_python(field_value)
                            # print("All OK with {}".format(a.code))
                        except:
                            if options['diagnostic']:
                                print('Issue with {} in {}'.format(field_name, a.code))
                                continue
                            else:
                                ts.update_from_db()
                                print('Synced {} from DB'.format(a.code))
                                continue
                        # print(clean_value)