from django.core.management.base import CommandError, BaseCommand


from activities.models import *

import logging

logger = logging.getLogger(__name__)

published_flag = {'false':False,'true':True}
flag = {'0':False,'1':True}

class Command(BaseCommand):
    """
    Remove curriculum placeholder content
    """

    help = 'Remove curriculum placeholder content'


    def handle(self, *args, **options):

        activities = 0
        for a in Activity.objects.all():
            try:
                if (len(str(a.curriculum[0].value)) < 100):
                    a.curriculum = None
                    a.save()
                    activities += 1
            except IndexError:
                pass
        self.stdout.write(f"Fixed {activities} activities")
