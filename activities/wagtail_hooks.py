from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin


from .models import Activity


class ActAdmin(ThumbnailMixin, ModelAdmin):
    model = Activity
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