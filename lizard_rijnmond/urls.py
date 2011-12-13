# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from lizard_rijnmond.views import segment_map
from lizard_rijnmond.views import water_level_map

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    url(r'^$',
        segment_map,
        name="segment_map"),
    url(r'^waterlevel/$',
        water_level_map,
        name="water_level_map"),
    )
