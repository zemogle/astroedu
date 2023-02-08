from django.core.management.base import CommandError, BaseCommand
from django.utils.text import slugify


from activities.models import *

import logging

logger = logging.getLogger(__name__)

published_flag = {'false':False,'true':True}
flag = {'0':False,'1':True}

class Command(BaseCommand):
    """
    Switch from using Institute to Organization (translated) for authors
    """

    help = 'Switch from using Institute to Organization (translated) for authors'


    def handle(self, *args, **options):
        for person in Person.objects.all():
            if not person.institution:
                continue
            try:
                org = Organization.objects.filter(name=person.institution.name)
                if org:
                    person.org = org[0]
                    person.save()
                else:
                    continue
            except Exception as e:
                print(e)
                print(person, person.institution.name)
