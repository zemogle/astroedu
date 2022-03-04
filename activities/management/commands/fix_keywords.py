import json
import os
import re
import sys
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
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
from wagtail.images.models import Image
from wagtail.documents.models import Document
from wagtail.users.models import UserProfile
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
        parser.add_argument("-l", "--lang", dest='lang', type=str, help="Import language version")
        parser.add_argument("-i", "--idcode", dest='code', type=str, help="Import specific activity by code and language version")

    def handle(self, *args, **options):
        codes = [lang[0] for lang in settings.LANGUAGES]
        if options['lang'] and options['lang'] in codes:
            lang = options['lang']
        else:
            lang = 'en'
        if options['code']:
            self.code = options['code']
        else:
            self.code = None
        old_pages = parse_fixture(filename='import_content/activities.json')
        activitypages, meta = parse_models(old_pages, lang=lang)
        self.metadata = meta
        # self.upload_categories()
        self.process_activity(activitypages=activitypages, lang=lang)

    def upload_categories(self):
        for k, cat in self.metadata.items():
            obj, c = Category.objects.get_or_create(name=cat)
            print(f"Adding {cat}")
        return

    def get_categories(self, categories):
        cids = []
        for c in categories:
            if self.metadata.get(c, None):
                cids.append(Category.objects.get(name=self.metadata.get(c)))
        return cids

    def process_activity(self, activitypages, lang):
        passed = []
        self.stdout.write("Processing Activities - {} in {}".format(len(activitypages), lang))

        for count,(key, fi) in enumerate(activitypages.items()):
            if self.code:
                if fi['code'] != self.code:
                    continue
                else:
                    print(f"Ingesting {self.code} in {lang}")
            else:
                print(f"Ingesting {count}")
            if fi['code'] == '1754' or fi['code'] == '0000':
                continue
            if not fi.get('language_code', None) or fi['language_code'] != lang or fi['code'] == '0000':
                passed.append(fi['code'])
                continue
            try:
                newactivity  = Activity.objects.get(code = fi['code'], locale__language_code=lang)
                new = False
                self.stdout.write(f"Updating {fi['code']}")
            except Activity.DoesNotExist:
                self.stdout.write(f"Cannot find {fi['code']}")
                continue

            print(fi['theme'])
            if fi['theme'] and fi['theme'] != 'NA':
                newactivity.theme = fi['theme']

            # for cat in self.get_categories(fi['astronomical_scientific_category']):
            #     newactivity.astro_category.add(cat)
            #     print(f"Added {cat.name} to {fi['code']}")

            # newactivity.keywords.add(*[x.strip() for x in fi['keywords'].split(',')])

            newactivity.save()
            self.stdout.write(f"Saved Categories for {newactivity.title}")

        print(f"Passed on {passed}")

def parse_fixture(filename):
    with open(filename,'r') as f:
        content = json.load(f)

    return content

def parse_models(old_pages, lang):
    activities = {}
    trans = {}
    metadata = {}
    for p in old_pages:
        if p['model'] == "activities.activity":
            activities[p['pk']] = p['fields']
        elif p['model'] == "activities.activitytranslation":
            if p['fields']["language_code"] == lang:
                trans[p['fields']['master']] = p['fields']
        elif p['model'] == "activities.metadataoption":
            if p['fields']['group'] == "astronomical_categories":
                metadata[p['pk']] = p['fields']['title']
    for k,v in activities.items():
        if trans.get(k):
            activities[k] = {**activities[k], **trans[k]}
    return activities, metadata


def html_or_rich(mdcontent, code=None):
    content = replace_images_with_embeds(markdown.markdown(mdcontent, extensions=['tables']), code)
    if not content:
        return [('htmltext', '')]
    elif content.find("<table") != -1 :
        return [('htmltext', content)]
    else:
        return [('richtext', RichText(content))]

def image_replace(value):
    new_start = 0
    result = ''
    for m in re.finditer(r'src="(.*?)".*?>', value):
        new_src = m.group(1)
        # Only replace image src if URL not DIVIO cloud hosting
        if new_src.startswith('https://astroedu-'):
            path = urlparse(new_src).path
        else:
            path = new_src.replace("http://astroedu.iau.org/",'').replace('media/','')
        imgid = import_image(path)
        if imgid:
            result += value[new_start:m.start()] + '<embed id="%s" embedtype="image" format="left" alt=""/>' % imgid
        new_start = m.end()
    result += value[new_start:]
    return value

def replace_images_with_embeds(content, code=None):
    soup = BeautifulSoup(content, 'html.parser')
    for img in soup.find_all("img"):
        if img['src'].startswith('https://astroedu-'):
            path = urlparse(img['src']).path
        else:
            path = img['src'].replace("http://astroedu.iau.org/",'').replace('media/','')
        imgid = import_image(path)
        if imgid:
            embed = soup.new_tag('embed')
            embed['format'] = 'fullwidth'
            embed['id'] = imgid
            embed['embedtype'] = 'image'
            embed['alt'] = path
            if img.parent == soup:
                soup.insert(0,embed)
                img.decompose()
            else:
                try:
                    img.parent.insert_after(embed)
                    img.decompose() # remove the unused img
                    # print(f'Replaced img with {imgid}')
                except Exception as e:
                    sys.stderr.write(str(e))
                    sys.stderr.write(str(embed)+"\n")
                    sys.stderr.write(str(code)+"\n")
                    raise
    return soup.prettify()

def import_image(filename):
    filename = filename.strip("/").replace('%20',' ')
    name = filename.split('/')[-1]
    if default_storage.exists(filename):
        imfile = ImageFile(file=default_storage.open(filename), name=name)
        image, c = Image.objects.get_or_create(file=imfile, title=name.rsplit('.',1)[0])
        image.save()
        return image.id
    else:
        return False

def import_attachments(activity, filename):
    filename = filename.strip("/").replace('%20',' ')
    name = filename.split('/')[-1]
    if default_storage.exists(filename):
        try:
            docfile = File(file=default_storage.open(filename),name=name)
            doc, c = Document.objects.get_or_create(file=docfile, title=name.rsplit('.',1)[0])
            doc.save()
        except Exception as e:
            print(f"Problem with {filename} in {activity}: {e}")
            return False
        obj, c = Attachment.objects.get_or_create(page=activity, document=doc)
        return True
    else:
        return False
