import io
import logging
from pathlib import Path
from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib.staticfiles import finders
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import activate, get_language
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import ModelChoiceIterator
from django.forms.widgets import (CheckboxSelectMultiple, RadioSelect, Select,
                                  SelectMultiple)
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase
from wagtail_localize.fields import SynchronizedField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, TranslatableMixin,  Orderable, Locale
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from weasyprint import HTML, CSS


from rest_framework import serializers

from activities import utils


class LocalizedSelectPanel(FieldPanel):
    """
    Customised FieldPanel to filter choices based on locale of page/model being created/edited
    Usage:
    widget_class - optional, override field widget type
                 - should be CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple
    typed_choice_field - set to True with Select widget forces drop down list
    """

    def __init__(self, field_name, widget_class=None, typed_choice_field=False, *args, **kwargs):
        if not widget_class in [None, CheckboxSelectMultiple, RadioSelect, Select, SelectMultiple]:
            raise ImproperlyConfigured(_(
                "widget_class should be a Django form widget class of type "
                "CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple"
            ))
        self.widget_class = widget_class
        self.typed_choice_field = typed_choice_field
        super().__init__(field_name, *args, **kwargs)

    def clone_kwargs(self):
        return {
            'heading': self.heading,
            'classname': self.classname,
            'help_text': self.help_text,
            'widget_class': self.widget_class,
            'typed_choice_field': self.typed_choice_field,
            'field_name': self.field_name,
        }

    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            if not self.panel.widget_class:
                self.form.fields[self.field_name].widget.choices=self.choice_list
            else:
                self.form.fields[self.field_name].widget = self.panel.widget_class(choices=self.choice_list)
            if self.panel.typed_choice_field:
                self.form.fields[self.field_name].__class__.__name__ = 'typed_choice_field'
            pass

        @property
        def choice_list(self):
            self.form.fields[self.field_name].queryset = self.form.fields[self.field_name].queryset.filter(locale_id=self.instance.locale_id)
            choices = ModelChoiceIterator(self.form.fields[self.field_name])
            return choices

def limit_lang_choice():
    limit = models.Q(locale__language_code=get_language())
    return limit

class BodyBlock(blocks.StreamBlock):
    richtext = blocks.RichTextBlock()
    htmltext = blocks.RawHTMLBlock()
    table =  TableBlock(template="activities/partials/table_template.html")

class ActivityHome(RoutablePageMixin, Page):
    @route(r'^a/(\d+)/(\w+)$')
    def activity_by_id(self, request, code=None, title=None):
        activity = Activity.objects.get(code=code)

        return self.render(request,
                context_overrides={'page': activity},
                template="activities/activity.html",)

class ActivityIndexPage(Page):
    about = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('about')
    ]

    def get_context(self, request):
        context = super().get_context(request)
        activities = Activity.objects.filter(locale=Locale.get_active()).order_by('-first_published_at')
        # Filter by tag
        params = ['keywords','category','level','skills','learning','age']
        context['facets'] = {param: {} for param in params}
        context['facets']['level'] = {'all': Level.objects.filter(locale=Locale.get_active()), 'name': 'Level' }
        context['facets']['category'] = {'all': Category.objects.filter(locale=Locale.get_active()), 'name': 'Category'}
        context['facets']['skills'] = {'all': Skills.objects.filter(locale=Locale.get_active()), 'name': 'Skills'}
        context['facets']['learning'] = {'all': Learning.objects.filter(locale=Locale.get_active()), 'name': 'Type of Learning'}
        context['facets']['age'] = {'all': Age.objects.filter(locale=Locale.get_active()), 'name': 'Age'}
        for param in params:
            if request.GET.get(param):
                activities = activities.filter(**{param+'__name':request.GET.get(param)})
                context['facets'][param]['selected'] = request.GET.get(param)
        context['activities'] = activities
        return context

class Keyword(TranslatableMixin, TaggedItemBase):
    content_object = ParentalKey('Activity', on_delete=models.CASCADE, related_name='keyword_items')

@register_snippet
class Category(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Scientific Category"
        verbose_name_plural = "Scientific Categories"
        unique_together = ('translation_key', 'locale')
        ordering = ['name',]

@register_snippet
class SciCategory(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "New Scientific Category"
        verbose_name_plural = "New Scientific Categories"
        unique_together = ('translation_key', 'locale')
        ordering = ['name',]


@register_snippet
class Location(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('translation_key', 'locale')
        ordering = ['name',]

@register_snippet
class Skills(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Skills"
        unique_together = ('translation_key', 'locale')
        ordering = ['name',]

@register_snippet
class Level(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Educational Level"
        unique_together = ('translation_key', 'locale')
        ordering = ['name',]

@register_snippet
class Learning(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Area of Learning"
        verbose_name_plural = "Areas of Learning"
        unique_together = ('translation_key', 'locale')
        ordering = ['name',]

@register_snippet
class Group(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

@register_snippet
class Supervised(TranslatableMixin):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Supervision"
        verbose_name_plural = "Supervision"
        unique_together = ('translation_key', 'locale')

@register_snippet
class Cost(TranslatableMixin):
    name = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField()
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order',]
        unique_together = ('translation_key', 'locale')

@register_snippet
class Age(TranslatableMixin):
    name = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField()
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order',]
        unique_together = ('translation_key', 'locale')

@register_snippet
class Time(TranslatableMixin):
    name = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField()
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Duration"
        verbose_name_plural = "Duration"
        unique_together = ('translation_key', 'locale')
        ordering = ['order',]

@register_snippet
class Organization(TranslatableMixin, models.Model):
    logo = models.ForeignKey('wagtailimages.Image', help_text="Logo or other image", null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    name = models.CharField(blank=False, max_length=255)
    fullname = models.CharField(max_length=255, blank=True, help_text='If set, the full name will be used in some places instead of the name', )
    country = CountryField(blank=True)
    url = models.URLField(blank=True, null=True, max_length=255 )
    about = RichTextField(blank=True)
    slug = models.CharField(max_length=255, help_text='URL slug for this page e.g. my-organization')

    @property
    def title(self):
        if self.fullname:
            return self.fullname
        else:
            return self.name

    def __str__(self):
        return self.name

    api_fields = [
            APIField('name'),
        ]

    class Meta:
        unique_together = [("translation_key", "locale"), ("slug", "locale")]
        ordering = ['name',]


@register_snippet
class Person(models.Model):
    name = models.CharField(blank=False, max_length=255)
    citable_name = models.CharField(blank=True, max_length=255, help_text='Required for astroEDU activities')
    email = models.EmailField(blank=True, null=True, max_length=255)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['name']


    def __str__(self):
        if self.org:
            return f"{self.name}, {self.org}"
        else:
            return f"{self.name}"


class AuthorInstitute(Orderable):
    activity = ParentalKey('activities.Activity', related_name='author_institute', on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)

    def display_name(self):
        # there were errors with no existing relations. Now display only relevant data
        display = []
        try:
            display.append(self.author.name)
        except:
            pass
        try:
            display.append(self.author.org.name)
        except:
            pass
        return ', '. join(display)

    def author_name(self):
        display = []
        try:
            display.append(self.author.name)
        except:
            pass
        return ', '. join(display)


    class Meta:
        verbose_name = "author"
        ordering = ['sort_order','author',]

    panels = [
        SnippetChooserPanel('author'),
    ]

    def __str__(self):
        return self.display_name()

class AuthorInstSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    class Meta:
        model = AuthorInstitute
        fields = (
            "author",
        )

class AgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Age
        fields = ("name",)

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ("name",)

class LearningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Learning
        fields = ("name",)

class CostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cost
        fields = ("name",)

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)

class SupervisedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervised
        fields = ("name",)

class TimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time
        fields = ("name",)

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("name",)

class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SciCategory
        fields = ("name",)

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skills
        fields = ("name",)

class Activity(Page):
    image = models.ForeignKey('wagtailimages.Image', help_text="Main image for listing pages", null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    abstract = RichTextField(blank=True, help_text='200 words', verbose_name='Abstract')
    theme = models.CharField(blank=True, max_length=40, help_text='Use top level AVM metadata')
    keywords = ClusterTaggableManager(through=Keyword, blank=True, verbose_name="Keywords")
    countries = CountryField(multiple=True, blank=True, help_text='Activity originally developed in')

    acknowledgement = models.CharField(blank=True, max_length=255)
    teaser = models.TextField(blank=True, verbose_name='Teaser', help_text='Maximum 2 sentences! Maybe what and how?')

    goals = RichTextField()
    objectives = RichTextField(verbose_name='Learning Objectives', )
    evaluation = StreamField(BodyBlock, help_text='If the teacher/educator wants to evaluate the impact of the activity, how can she/he do it?')
    materials = StreamField(BodyBlock, blank=True, verbose_name='List of material', help_text='Please indicate costs and/or suppliers if possible')
    background = StreamField(BodyBlock, verbose_name='Background Information', )
    fulldesc = StreamField(BodyBlock, verbose_name='Full description of the activity')
    curriculum = StreamField(BodyBlock, blank=True, null=True, verbose_name='Connection to school curriculum', help_text='Please indicate which country')
    additional_information = StreamField(BodyBlock, blank=True, help_text='Notes, Tips, Resources, Follow-up, Questions, Safety Requirements, Variations')
    conclusion = RichTextField(blank=True)

    short_desc_material = RichTextField(blank=True, verbose_name='Short description of Suplementary material')
    further_reading = RichTextField(blank=True, verbose_name='Further reading', default='')
    reference = RichTextField(blank=True, verbose_name='References')

    code = models.CharField(max_length=4, help_text='The 4 digit code that identifies the Activity, in the format "YY##": year, folowed by sequential number.')
    doi = models.CharField(blank=True, max_length=50, verbose_name='DOI', help_text='Digital Object Identifier, in the format XXXX/YYYY. See http://www.doi.org/')

    pdf = models.ForeignKey('wagtaildocs.Document', null=True, blank=True, on_delete=models.SET_NULL, help_text="PDF will be autogenerated after publication. Do not upload one." )

# Meta data
    astro_category = ParentalManyToManyField(Category, blank=True, verbose_name='Old Scientific Categories')
    category = ParentalManyToManyField(SciCategory, blank=True, verbose_name='Scientific Categories')

    age = ParentalManyToManyField('activities.Age',blank=True)
    level = ParentalManyToManyField(Level, help_text='Specify at least one of "Age" and "Level". ', verbose_name='Education level', blank=True)
    time = models.ForeignKey(Time, on_delete=models.SET_NULL, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Group or individual activity')
    supervised = models.ForeignKey(Supervised, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Supervised for safety')
    cost = models.ForeignKey(Cost, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Cost per student')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    skills = ParentalManyToManyField(Skills, blank=True, verbose_name='core skills')
    learning = ParentalManyToManyField(Learning, blank=True, verbose_name='type of learning activity', help_text='Enquiry-based learning model')

    featured = models.BooleanField(default=False, help_text="Feature on homepage")

    original_author = models.CharField(max_length=255,
                    blank=True,
                    null=True,
                    help_text='Original Author of the activity (if not the authors listed above')

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('featured'),
            FieldPanel('code'),
            FieldPanel('doi'),
            FieldPanel('pdf'),
            FieldPanel('theme'),
            FieldPanel('abstract'),
            FieldPanel('acknowledgement'),
            FieldPanel('teaser'),
            FieldPanel('image'),
        ], heading="Core Information"),
        MultiFieldPanel([
            InlinePanel('author_institute', label="Author(s)"),
            FieldPanel('countries')
        ], heading="Authors"),
        MultiFieldPanel([
            FieldPanel('goals'),
            FieldPanel('objectives'),
            FieldPanel('evaluation'),
            FieldPanel('materials'),
            FieldPanel('background'),
            FieldPanel('fulldesc'),
            FieldPanel('curriculum'),
            FieldPanel('additional_information'),
            FieldPanel('conclusion'),
            FieldPanel('short_desc_material'),
            FieldPanel('further_reading'),
            FieldPanel('reference'),
            InlinePanel('attachment_documents', label="Attachment(s)"),
        ], heading="Activity Information"),
        MultiFieldPanel([
            LocalizedSelectPanel('category',widget_class=CheckboxSelectMultiple,),
            FieldPanel('location', widget=forms.Select),
            LocalizedSelectPanel('location',widget_class=Select,),
            FieldPanel('keywords'),
            LocalizedSelectPanel('age',widget_class=CheckboxSelectMultiple,),
            LocalizedSelectPanel('level',widget_class=CheckboxSelectMultiple,),
            LocalizedSelectPanel('time',widget_class=Select,),
            LocalizedSelectPanel('group',widget_class=Select,),
            LocalizedSelectPanel('supervised',widget_class=Select,),
            LocalizedSelectPanel('cost',widget_class=Select,),
            LocalizedSelectPanel('skills',widget_class=CheckboxSelectMultiple,),
            LocalizedSelectPanel('learning',widget_class=CheckboxSelectMultiple,),
        ], heading="Meta data")
    ]

    api_fields = [
        APIField('title'),
        APIField('teaser'),
        APIField('theme'),
        APIField('pdf'),
        APIField('image'),
        APIField('author_institute', serializer=AuthorInstSerializer(many=True)),
        APIField('category', serializer=CatSerializer(many=True)),
        APIField('doi'),
        APIField('level', serializer=LevelSerializer(many=True)),
        APIField('age', serializer=AgeSerializer(many=True)),
        APIField('learning', serializer=LearningSerializer(many=True)),
        APIField('cost', serializer=CostSerializer()),
        APIField('time', serializer=TimeSerializer()),
        APIField('supervised', serializer=SupervisedSerializer()),
        APIField('location', serializer=LocationSerializer()),
        APIField('group', serializer=GroupSerializer()),
        APIField('skills', serializer=SkillSerializer(many=True)),

    ]

    override_translatable_fields = [
        SynchronizedField("slug"),
        SynchronizedField("code"),
    ]

    search_fields = Page.search_fields + [ # Inherit search_fields from Page
        index.SearchField('teaser'),
        index.SearchField('theme'),
        index.SearchField('background'),
        index.SearchField('fulldesc'),
    ]

    # template = "activities/activity_detail_print.html"
    def age_range(self):
        age_ranges = [obj.name for obj in self.age.all()]
        return utils.beautify_age_range(age_ranges)

    def levels_joined(self):
        levels = [obj.name for obj in self.level.all()]
        return ', '.join(levels)

    def skills_joined(self):
        skills = [obj.name for obj in self.skills.all()]
        return ', '.join(skills)

    def learning_joined(self):
        learning = [obj.name for obj in self.learning.all()]
        return ', '.join(learning)

    def categories_joined(self):
        astro_category = [obj.name for obj in self.category.all()]
        return ', '.join(astro_category)
    
    def categories_joined_links(self):
        astro_category = [obj.name for obj in self.category.all()]
        return ', '.join(astro_category)

    @property
    def updated_date(self):
        if self.go_live_at and self.go_live_at > self.first_published_at +timedelta(seconds=3600):
            return self.go_live_at
        else:
            return False

    @property
    def sort_date(self):
        if self.go_live_at and self.go_live_at > self.first_published_at +timedelta(seconds=3600):
            return self.go_live_at
        else:
            return self.first_published_at

    @property
    def author_inst_list(self):
        result = []
        for item in self.author_institute.all():
            result.append(item.display_name())
        return '; '.join(result)

    @property
    def author_list(self):
        result = []
        for item in self.author_institute.all():
            result.append(item.author.name)
        return '; '.join(result)

    def citable_author_list(self):
        result = []
        for item in self.author_institute.all():
            result.append(item.author.citable_name)
        return '; '.join(result)

    def keywords_joined(self):
        return ", ".join([k.name for k in self.keywords.all()])

    def generate_pdf(self, path='', lang_code='en'):
        activate(lang_code)
        context = {
            'page': self,
            'pdf': True,
            'media_root' : settings.MEDIA_ROOT,
            'sections': self.sections,
            'meta' : self.meta,
            'long_meta' : ['skills','learning']
        }
        with open(finders.find('css/print.css')) as f:
            css = CSS(string=f.read())
        html_string = render_to_string('activities/activity_detail_print.html', context)
        html = HTML(string=html_string, base_url="https://astroedu.iau.org")
        fileobj = io.BytesIO()
        html.write_pdf(fileobj, stylesheets=[css])
        # return filepath
        pdf = fileobj.getvalue()
        fileobj.close()
        if path:
            filepath = Path(path) / filename
            Path(outfile).write_bytes(pdf)
            return filepath
        else:
            return pdf

    @property
    def sections(self):
        return [
                {'code':'materials', 'text':_('Materials'),'content':self.materials,'stream':True},
                {'code':'goals', 'text':_('Goals'),'content':self.goals,'stream':False},
                {'code':'objectives','text':_('Learning Objectives'),'content': self.objectives, 'stream':False},
                {'code':'background', 'text':_('Background'),'content':self.background,'stream':True},
                {'code':'fulldesc', 'text':_('Full Description'), 'content':self.fulldesc,'stream':True},
                {'code':'evaluation', 'text':_('Evaluation'), 'content':self.evaluation,'stream':True},
                {'code':'curriculum', 'text':_('Curriculum'), 'content':self.curriculum,'stream':True},
                {'code':'additional_information', 'text':_('Additional Information'), 'content':self.additional_information,'stream':True},
                {'code':'conclusion', 'text':_('Conclusion'), 'content':self.conclusion,'stream':False},
                {'code':'further_reading', 'text':_('Further Reading'), 'content':self.further_reading,'stream':False},
        ]

    def meta(self):
        return [
                {'code':'category', 'text': _('Category'), 'content':self.category.all(), 'links':True},
                {'code':'location', 'text': _('Location'), 'content':self.location},
                {'code':'age', 'text': _('Age'), 'content':self.age_range()},
                {'code':'level', 'text': _('Level'), 'content':self.level.all(), 'links':True},
                {'code':'time', 'text': _('Time'), 'content':self.time},
                {'code':'group', 'text': _('Group'), 'content':self.group},
                {'code':'supervised', 'text': _('Supervised'), 'content':self.supervised},
                {'code':'cost', 'text': _('Cost'), 'content':self.cost},
                {'code':'skills', 'text': _('Skills'), 'content':self.skills.all(), 'links':True},
                {'code':'learning', 'text': _('Type of Learning'), 'content':self.learning.all(), 'links':True},
        ]

    def get_context(self, request):
        context = super().get_context(request)
        context['sections']  = self.sections
        context['meta'] = self.meta
        return context
    
    @property
    def languages(self):
        locales = Locale.objects.all()
        return ", ".join([l.language_code for l in locales if self.has_translation(locale=l)])

class Attachment(Orderable):
    page = ParentalKey(Activity, on_delete=models.CASCADE, related_name='attachment_documents')
    document =  models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='attachments'
    )

    panels = [
        FieldPanel('document'),
    ]

class CollectionIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

class Collection(Page):
    description = RichTextField(blank=True, verbose_name='brief description', )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('image'),
        InlinePanel('activity_pages', label="Activity Pages")
    ]

    @property
    def code(self):
        return self.slug

    @property
    def main_visual(self):
        return self.image.file if self.image else None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
#        tasks.make_thumbnail.delay(self)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('collections:detail', args=[self.slug])

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        activities = self.activity_pages.all().order_by('activity__title')

        context['activities'] = activities
        return context

class CollectionPage(Orderable):
    page = ParentalKey(Collection, on_delete=models.CASCADE, related_name='activity_pages')
    activity = models.ForeignKey(Activity, related_name='+', on_delete=models.SET_NULL, null=True)

    panels = [
        FieldPanel('activity'),
    ]
