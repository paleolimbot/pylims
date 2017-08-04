from django.shortcuts import render
from django.views import generic
from . import models

# Create your views here.


def index(request):
    return render(request, 'pylims/index.html')


class ProjectListView(generic.ListView):
    template_name = 'pylims/project_list.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return models.Project.objects.all


class ProjectDetailView(generic.DetailView):
    model = models.Project
    template_name = 'pylims/project.html'


class LocationListView(generic.ListView):
    template_name = 'pylims/location_list.html'
    context_object_name = 'location_list'

    def get_queryset(self):
        return models.Location.objects.all


class LocationDetailView(generic.DetailView):
    model = models.Location
    template_name = 'pylims/location.html'


class ParameterListView(generic.ListView):
    template_name = 'pylims/parameter_list.html'
    context_object_name = 'parameter_list'

    def get_queryset(self):
        return models.Parameter.objects.all


class ParameterDetailView(generic.DetailView):
    model = models.Parameter
    template_name = 'pylims/parameter.html'


class SampleListView(generic.ListView):
    template_name = 'pylims/sample_list.html'
    context_object_name = 'sample_list'

    def get_queryset(self):
        return models.Sample.objects.all


class SampleDetailView(generic.DetailView):
    template_name = 'pylims/sample.html'
    model = models.Sample

