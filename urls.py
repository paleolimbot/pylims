
from django.conf.urls import url
from . import views

app_name = 'pylims'
urlpatterns = [
    # the index page
    url(r'^$', views.index),
    url(r'^project/$', views.ProjectListView.as_view(), name="project_list"),
    url(r'^project/(?P<pk>[0-9]+)$', views.ProjectDetailView.as_view(), name="project_detail"),
    url(r'^location/$', views.LocationListView.as_view(), name="location_list"),
    url(r'^location/(?P<pk>[0-9]+)$', views.LocationDetailView.as_view(), name="location_detail"),
    url(r'^samplemetakey/$', views.SampleMetaKeyListView.as_view(), name="samplemetakey_list"),
    url(r'^samplemetakey/(?P<pk>[0-9]+)$', views.SampleMetaKeyDetailView.as_view(), name="samplemetakey_detail"),
    url(r'^sample/$', views.SampleListView.as_view(), name="sample_list"),
    url(r'^sample/(?P<pk>[0-9]+)$', views.SampleDetailView.as_view(), name="sample_detail"),
]
