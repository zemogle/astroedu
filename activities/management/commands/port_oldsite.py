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
        parser.add_argument("-p", "--people", dest='people', action='store_true', help="Import just people")

    def handle(self, *args, **options):
        codes = [lang[0] for lang in settings.LANGUAGES]
        if options['lang'] and options['lang'] in codes:
            code = options['lang']
        else:
            code = 'en'
        old_pages = parse_fixture(filename='import_content/activities.json')
        activitypages, trans, meta, authors, institutes = join_activites(old_pages, lang=code)
        self.upload_people(institutes)
        sys.exit()
        if options['people']:
            sys.exit()
        l, c = Locale.objects.get_or_create(language_code=code)
        self.metainfo = self.process_meta(lang=code, metainfo=meta)
        self.process_activity(lang=code, authors=authors)

    def process_meta(self, lang, metainfo):
        group = {'time':Time,
                'supervised':Supervised,
                'skills':Skills,
                'location':Location,
                'level':Level,
                'learning':Learning,
                'group':Group,
                'cost':Cost,
                'categories':Category,
                'age':Age}
        # Translate old category IDs in new category iDs
        for id, meta in metainfo.items():
            try:
                obj, c = group[meta['group']].objects.get_or_create(name=meta['title'])
            except KeyError as e:
                print(f"{e}")
                continue
            meta['newid'] = obj.id
        return metainfo

    def get_categories(self, categories, obj):
        cids = []
        for c in categories:
            if self.metainfo.get(c, None):
                try:
                    cid = self.metainfo.get(c)['newid']
                except:
                    continue
                cids.append(cid)
        return obj.objects.filter(id__in=cids)

    def process_activity(self, lang, authors):
        passed = []
        self.stdout.write("Processing Activities - {} in {}".format(len(activitypages), lang))
        try:
            activityhome = ActivityHome.objects.get(title="Activities", locale__language_code=lang)
        except ActivityHome.DoesNotExist:
            activityhome = ActivityHome(title="Activities")
            homepage = HomePage.objects.get(locale__language_code=lang)
            homepage.add_child(instance=activityhome)
            homepage.save()
        for count,(key, fi) in enumerate(activitypages.items()):
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
                newactivity  = Activity(code = fi['code'])
                self.stdout.write(f"Creating {fi['code']}")
                new = True
            print(f"{fi['title']}")
            newactivity.title = fi['title']
            newactivity.abstract = RichText(markdown.markdown(fi['abstract']))
            newactivity.fulldesc = html_or_rich(fi['fulldesc'], 'fulldesc')
            newactivity.goals = RichText(markdown.markdown(fi['goals']))
            newactivity.objectives = RichText(markdown.markdown(fi['objectives']))
            newactivity.teaser = fi['teaser']
            newactivity.acknowledgement = fi['acknowledgement']
            newactivity.evaluation = html_or_rich(fi['evaluation'], 'eval')
            newactivity.materials = html_or_rich(fi['materials'], 'material')
            newactivity.background = html_or_rich(fi['background'], 'bg')
            newactivity.curriculum = html_or_rich(fi['curriculum'], 'curric')
            newactivity.additional_information = html_or_rich(fi['additional_information'])
            newactivity.conclusion = RichText(markdown.markdown(fi['conclusion']))
            newactivity.short_desc_material = RichText(markdown.markdown(fi['short_desc_material']))
            newactivity.further_reading = RichText(markdown.markdown(fi['further_reading']))
            newactivity.reference = RichText(markdown.markdown(fi['reference']))
            newactivity.doi = fi['doi']
            newactivity.first_published_at = fi['creation_date']
            newactivity.live = fi['published']
            newactivity.latest_revision_created_at = fi['modification_date']
            newactivity.go_live_at = fi["release_date"]
            newactivity.slug = fi['code']
            newactivity.time = self.get_categories([fi['time']], Time)[0]
            newactivity.group = self.get_categories([fi['group']], Group)[0]
            newactivity.supervised = self.get_categories([fi['supervised']], Supervised)[0]
            newactivity.cost = self.get_categories([fi['cost']], Cost)[0]
            newactivity.location = self.get_categories([fi['location']], Location)[0]

            if new:
                activityhome.add_child(instance=newactivity)
                activityhome.save()
                self.stdout.write(f"Saved {newactivity.title}")

            newactivity.astro_category.add(*list(self.get_categories(fi['astronomical_scientific_category'], Category)))
            newactivity.age.add(*list(self.get_categories(fi['age'], Age)))
            newactivity.level.add(*list(self.get_categories(fi['level'], Level)))
            newactivity.skills.add(*list(self.get_categories(fi['skills'], Skills)))
            newactivity.learning.add(*list(self.get_categories(fi['learning'], Learning)))

            newactivity.keywords.add(*[x.strip() for x in fi['keywords'].split(',')])

            newactivity.save()
            self.stdout.write(f"Saved Categories for {newactivity.title}")

            self.add_authors(key, newactivity, authors)
            self.stdout.write(f"Saved Author for {newactivity.title}")
        print(f"Passed on {passed}")

    def add_authors(self, oldid, activity, authors):
        for author in authors[oldid]:
            auth, c = AuthorInstitute.objects.get_or_create(activity=activity,author=self.persons[author])
        return

    def upload_people(self, institutes):
        inst = {}
        persons = {}
        people = parse_fixture(filename='import_content/institutions.json')
        for p in people:
            if p['model'] == "institutions.institution":
                i, c = Institute.objects.get_or_create(
                    name = p['fields']['name'],
                    fullname = p['fields']['fullname'],
                    url = p['fields']['url']
                )
                inst[p['pk']] = i
                self.stdout.write(f"Added {i.name}")
        self.institutes = inst
        for p in people:
            if p['model'] == "institutions.person":
                person, c = Person.objects.get_or_create(
                    name = p['fields']['name'],
                    citable_name = p['fields']['citable_name'],
                    email = p['fields']['email'],
                    )
                try:
                    person.institution = inst[institutes[p['pk']]]
                    person.save()
                except Exception as e:
                    print(f"Institution ID {e} not found")
                self.stdout.write(f"Added {person.name} at {person.institution}")
                persons[p['pk']] = person
        self.persons = persons
        return

def parse_fixture(filename):
    with open(filename,'r') as f:
        content = json.load(f)

    return content

def join_activites(old_pages, lang):
    activities = {}
    trans = {}
    metadata = {}
    authors = {}
    institutes = {}
    for p in old_pages:
        if p['model'] == "activities.activity":
            activities[p['pk']] = p['fields']
        elif p['model'] == "activities.activitytranslation":
            if p['fields']["language_code"] == lang:
                trans[p['fields']['master']] = p['fields']
        elif p['model'] == "activities.metadataoption":
            metadata[p['pk']] = p['fields']
        elif p['model'] == "activities.authorinstitution":
            if authors.get(p['fields']['activity'], None):
                authors[p['fields']['activity']].append(p['fields']['author'])
            else:
                authors[p['fields']['activity']] = [p['fields']['author']]
            # Institute ID by author ID
            institutes[p['fields']['author']] = p['fields']['institution']
    for k,v in activities.items():
        if trans.get(k):
            activities[k] = {**activities[k], **trans[k]}
    return activities, trans, metadata, authors, institutes


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
        imgid = '1' #import_image(path)
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
                    print(f'Replaced img with {imgid}')
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
        image = Image(file=ImageFile(file=default_storage.open(filename), name=name), title=name.rsplit('.',1)[0])
        image.save()
        return image.id
    else:
        return False

def import_attachments(filename):
    filename = filename.strip("/").replace('%20',' ')
    name = filename.split('/')[-1]
    if default_storage.exists(filename):
        image = Image(file=ImageFile(file=default_storage.open(filename), name=name), title=name.rsplit('.',1)[0])
        image.save()
        return image.id
    else:
        return False
