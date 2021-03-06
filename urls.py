
from django.conf.urls import url
from . import views

app_name = 'pylims'
urlpatterns = [
    # the index page
    url(r'^$', views.index, name="index"),
    url(r'^project/$', views.ProjectListView.as_view(), name="project_list"),
    url(r'^project/(?P<pk>[0-9]+)$', views.ProjectDetailView.as_view(), name="project_detail"),
    url(r'^location/$', views.LocationListView.as_view(), name="location_list"),
    url(r'^location/(?P<pk>[0-9]+)$', views.LocationDetailView.as_view(), name="location_detail"),
    url(r'^parameter/$', views.ParameterListView.as_view(), name="parameter_list"),
    url(r'^parameter/(?P<pk>[0-9]+)$', views.ParameterDetailView.as_view(), name="parameter_detail"),
    url(r'^user/$', views.UserListView.as_view(), name="user_list"),
    url(r'^user/(?P<pk>[0-9]+)$', views.UserDetailView.as_view(), name="user_detail"),
    url(r'^sample/$', views.SampleListView.as_view(), name="sample_list"),
    url(r'^sample/add$', views.SampleCreateView.as_view(), name="sample_create"),
    url(r'^sample/import$', views.SampleImportView.as_view(), name="sample_import"),
    url(r'^data_import/$', views.DataImportListView.as_view(), name="data_import_list"),
    url(r'^data_import/(?P<pk>[0-9]+)$', views.DataImportDetailView.as_view(), name="data_import_detail"),
    url(r'^data_import/(?P<pk>[0-9]+)/apply$', views.apply_data_import, name="data_import_apply"),
    url(r'^sample/(?P<pk>[0-9]+)$', views.SampleDetailView.as_view(), name="sample_detail"),
]
