from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from .api import api_router

from search import views as search_views
from activities.views import CollectionListView, ActivityListView, ActivityDetailView, \
    OrganizationListView, OrganizationDetail

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('api/', api_router.urls),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('search/', search_views.search, name='search'),
    path('activities/',ActivityListView.as_view(), name='activitylist'),
    path('activities/<slug:code>/<slug:slug>/', ActivityDetailView.as_view(), name="activitydetail"),
    path('activities/<slug:code>/', ActivityDetailView.as_view(), name="activitydetail_short"),
    path('partners/', OrganizationListView.as_view(), name='orglist'),
    path('partners/<slug:slug>/', OrganizationDetail.as_view(), name='orgdetail'),
    path("", include(wagtail_urls)),
)
