from django.shortcuts import render
from django.views import generic
from django.contrib.auth.models import User
from . import models

# Create your views here.


def index(request):
    return render(request, 'pylims/index.html')


class ProjectListView(generic.ListView):
    template_name = 'pylims/project_list.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return models.Project.objects.all()


class ProjectDetailView(generic.DetailView):
    model = models.Project
    template_name = 'pylims/project.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['sample_list_title'] = "Project Samples"
        context['sample_list'] = models.Sample.objects.filter(project=context['project'])
        return context


class LocationListView(generic.ListView):
    template_name = 'pylims/location_list.html'
    context_object_name = 'location_list'

    def get_queryset(self):
        return models.Location.objects.all()


class LocationDetailView(generic.DetailView):
    model = models.Location
    template_name = 'pylims/location.html'

    def get_context_data(self, **kwargs):
        context = super(LocationDetailView, self).get_context_data(**kwargs)
        context['sample_list_title'] = "Samples from %s" % context['location'].name
        context['sample_list'] = models.Sample.objects.filter(location=context['location'])
        return context


class ParameterListView(generic.ListView):
    template_name = 'pylims/parameter_list.html'
    context_object_name = 'parameter_list'

    def get_queryset(self):
        return models.Parameter.objects.all()


class ParameterDetailView(generic.DetailView):
    model = models.Parameter
    template_name = 'pylims/parameter.html'

    def get_context_data(self, **kwargs):
        context = super(ParameterDetailView, self).get_context_data(**kwargs)
        context['sample_list_title'] = "Samples with %s" % context['parameter'].name
        context['sample_list'] = models.Sample.objects.filter(measurement__param=context['parameter'])
        return context


class UserListView(generic.ListView):
    template_name = 'pylims/user_list.html'

    def get_queryset(self):
        return User.objects.all()


class UserDetailView(generic.DetailView):
    model = User
    template_name = 'pylims/user.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['sample_list_title'] = "Samples created by %s" % context['user'].username
        context['sample_list'] = models.Sample.objects.filter(user=context['user'])
        return context


class SampleListView(generic.ListView):
    template_name = 'pylims/sample_list.html'
    context_object_name = 'sample_list'

    def get_queryset(self):
        return models.Sample.objects.all()


class SampleDetailView(generic.DetailView):
    template_name = 'pylims/sample.html'
    model = models.Sample



