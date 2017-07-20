
from django.conf.urls import url
from . import views

app_name = 'pylims'
urlpatterns = [
    # the index page
    url(r'^$', views.index),
]
