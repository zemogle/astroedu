from django.db import models

from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page, Locale

from activities.models import Activity, BodyBlock

class HomePage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        context['featured'] = Activity.objects.filter(featured=True, locale=Locale.get_active()).live()
        return context

class ContentPage(Page):
    summary = RichTextField("optional summary/teaser", blank=True)
    content = StreamField(BodyBlock, use_json_field=True)

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('image'),
        FieldPanel('summary'),
        FieldPanel('content'),
    ]

    api_fields = [
        APIField('title'),
        APIField('summary'),
        APIField('content'),
    ]

class NewsIndexPage(Page):
    intro = RichTextField("optional summary/teaser", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['newspages'] = NewsPage.objects.filter(locale=Locale.get_active())
        return context

class NewsPage(Page):
    summary = RichTextField("optional summary/teaser", blank=True)
    content = StreamField(BodyBlock, use_json_field=True)

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('image'),
        FieldPanel('summary'),
        FieldPanel('content'),
    ]
