import json
import os
import re
import sys
from urllib.parse import urlparse
from collections import Counter
import polib

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
from wagtail_localize.segments.extract import *

from wagtail_localize.segments.types import OverridableSegmentValue, TemplateSegmentValue

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
        parser.add_argument("-c", "--code", dest='code', type=int, help="Activity code")

    def handle(self, *args, **options):

        # Activity list
        activities = ActivityHome.objects.get(title='Activities').get_children()
        activities_it = ActivityHome.objects.get(title='Activities IT').get_children()

        code = options.get('code', None)
        if not code:
            activity_list = [a.activity for a in activities]
        else:
            activity = activities.get(activity__code=code).activity
            activity_list = [activity]
        for activity in activity_list:
            code = activity.code
            self.stdout.write(f"Translating {code} - {activity.title}")
            try:
                activity_it = activities_it.get(activity__code=code).activity
            except:
                self.stderr.write(f'Activity {code} not found')
                continue
            key = activity.translation_key
            tr = Translation.objects.get(source__object_id=key)
            segments = tr.export_po()

            translation = extract_segments(activity_it)
            translation = self.strip_translation(translation)

            po = self.reformat_po(segments, translation)
            tr.import_po(po=po)
            try:
                tr.save_target()
            except Exception as e:
                self.stderr.write(str(e))

    def reformat_po(self, segments, translation):
        po = polib.POFile()
        po.metadata = segments.metadata
        segnames = Counter([s.msgctxt for s in segments])
        transnames = Counter([s.path for s in translation])
        for segname, count in segnames.items():
            # find all segments with same name
            seggroup = [s for s in segments if s.msgctxt == segname]
            # Find translation segments with name and filter templatesegmens out
            if "." in segname:
                segname = segname.split('.')[0]
            seg_trans = [s for s in translation if segname in s.path]
            seg_trans = [s for s in seg_trans if type(s) != TemplateSegmentValue]
            count_trans = len(seg_trans)
            # print(f"{segname}: {count} ? {count_trans}")
            for i, segment in enumerate(seggroup):
                ind = i + 1
                # print(ind, count_trans)
                if  ind > count_trans:
                    segment.msgstr = '-'
                elif ind == count_trans and count_trans > count:
                    segment.msgstr = " ".join([txt for txt.string.data in seg_trans[ind:-1]])
                elif type(seg_trans[i]) == OverridableSegmentValue:
                    segment.msgstr = seg_trans[i].data
                else:
                    segment.msgstr = seg_trans[i].string.data
                # print(f"{segment.msgctxt} -> {segment.msgstr}")
                po.append(segment)
        return po

    def strip_translation(self, translation):
        new_trans = []
        exclusions = ['cost','group','image','location','supervised','theme','time']
        for trans in translation:
            if trans.path not in exclusions and 'keyword_items' not in trans.path:
                new_trans.append(trans)
        return new_trans
