from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.helpers import ButtonHelper

from django.urls import reverse

from .models import Activity

import logging

class DateButtonHelper(ButtonHelper):

    view_button_classnames = ['button', 'no button-small', 'button-secondary'] 

    def view_button(self, obj):
        # Define a label for our button
        text = 'Reset date'
        return {
            'url': reverse('activityresetdate', args=(obj.pk,)),
            'label': text,
            'classname': self.finalise_classname(self.view_button_classnames),
            'title': "Reset activity published date",
        }

    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None, classnames_exclude=None):
        btns = super().get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)
        if 'view' not in (exclude or []):
            btns.append(
                self.view_button(obj)
            )
        return btns

class ActAdmin(ThumbnailMixin, ModelAdmin):
    model = Activity
    button_helper_class = DateButtonHelper
    menu_label = 'Activities'  # ditch this to use verbose_name_plural from model
    menu_icon = 'pilcrow'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('admin_thumb','title', 'code','languages', 'sort_date')
    search_fields = ('title', 'code')
    thumb_image_field_name = 'image'
    thumb_default = 'https://via.placeholder.com/100x100.png?text=No+Image+Set'

    # def languages(self, obj):
    #     return obj.get_languages()
    #     # return 
    # languages.short_description = 'Languages'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show people managed by the current user
        codes = set(list(qs.values_list('code', flat=True)))
        return Activity.objects.filter(code__in=codes).order_by('-code')

# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(ActAdmin)