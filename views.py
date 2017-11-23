
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.utils.http import urlencode
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from . import models
from .query_string_filter import filter_sample_table

# Create your views here.


@login_required
def index(request):
    return render(request, 'pylims/index.html')


class ProjectListView(LoginRequiredMixin, generic.ListView):
    template_name = 'pylims/project_list.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return models.Project.objects.all()


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Project
    template_name = 'pylims/project.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['sample_list_title'] = "Project Samples"
        context['sample_list'] = models.Sample.objects.filter(project=context['project'])
        # apply sample list filtering based on query string params
        sample_list_context = filter_sample_table(context['sample_list'], self.request.GET)
        context.update(sample_list_context)
        return context


class LocationListView(LoginRequiredMixin, generic.ListView):
    template_name = 'pylims/location_list.html'
    context_object_name = 'location_list'

    def get_queryset(self):
        return models.Location.objects.all()


class LocationDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Location
    template_name = 'pylims/location.html'

    def get_context_data(self, **kwargs):
        context = super(LocationDetailView, self).get_context_data(**kwargs)
        context['sample_list_title'] = "Samples from %s" % context['location'].name
        context['sample_list'] = models.Sample.objects.filter(location=context['location'])
        # apply sample list filtering based on query string params
        sample_list_context = filter_sample_table(context['sample_list'], self.request.GET)
        context.update(sample_list_context)
        return context


class ParameterListView(LoginRequiredMixin, generic.ListView):
    template_name = 'pylims/parameter_list.html'
    context_object_name = 'parameter_list'

    def get_queryset(self):
        return models.Parameter.objects.all()


class ParameterDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Parameter
    template_name = 'pylims/parameter.html'

    def get_context_data(self, **kwargs):
        context = super(ParameterDetailView, self).get_context_data(**kwargs)
        context['sample_list_title'] = "Samples with %s" % context['parameter'].name
        context['sample_list'] = models.Sample.objects.filter(measurement__param=context['parameter'])
        # apply sample list filtering based on query string params
        sample_list_context = filter_sample_table(context['sample_list'], self.request.GET)
        context.update(sample_list_context)
        return context


class UserListView(LoginRequiredMixin, generic.ListView):
    template_name = 'pylims/user_list.html'

    def get_queryset(self):
        return User.objects.all()


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'pylims/user.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['sample_list_title'] = "Samples created by %s" % context['user'].username
        context['sample_list'] = models.Sample.objects.filter(user=context['user'])
        # apply sample list filtering based on query string params
        sample_list_context = filter_sample_table(context['sample_list'], self.request.GET)
        context.update(sample_list_context)
        return context


class SampleListView(LoginRequiredMixin, generic.ListView):
    template_name = 'pylims/sample_list.html'
    context_object_name = 'sample_list'

    def get_queryset(self):
        return models.Sample.objects.all()

    def get_context_data(self, **kwargs):
        context = super(SampleListView, self).get_context_data(**kwargs)
        # apply sample list filtering based on query string params
        sample_list_context = filter_sample_table(context['sample_list'], self.request.GET)
        context.update(sample_list_context)
        return context


class SampleDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'pylims/sample.html'
    model = models.Sample


class SampleCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Sample
    fields = ['name', 'collected', 'project', 'location']
    success_url = reverse_lazy('pylims:sample_list')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # set the created by user using the request
        form.instance.user = self.request.user
        return super(SampleCreateView, self).form_valid(form)


class SampleImportView(LoginRequiredMixin, generic.CreateView):
    model = models.DataImport
    fields = ['driver', 'text']
    template_name = "pylims/sample_import_form.html"

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # set the created by user using the request
        form.instance.user = self.request.user
        return super(SampleImportView, self).form_valid(form)


class DataImportListView(LoginRequiredMixin, generic.ListView):
    template_name = 'pylims/data_import_list.html'

    def get_queryset(self):
        return models.DataImport.objects.all()


class DataImportDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.DataImport
    template_name = 'pylims/data_import.html'

    def get_context_data(self, **kwargs):
        context = super(DataImportDetailView, self).get_context_data(**kwargs)

        # different contexts for imported versus non-imported data imports
        if context['dataimport'].applied:
            # get matching samples
            context['sample_list'] = models.Sample.objects.filter(data_import=context['dataimport'])
            # apply sample list filtering based on query string params
            sample_list_context = filter_sample_table(context['sample_list'], self.request.GET)
            # set sample table title
            context['sample_list_title'] = "Imported samples"
            context.update(sample_list_context)
        else:
            # get the preview context
            context.update(self.preview_context(context))

        return context

    def preview_context(self, context):
        # run import in preview mode
        result = context['dataimport'].apply_import(save=False)

        # classify result by object type and if it currently exists or not
        out_dict = {'objects': {}, 'tags': {}}
        for item in result:
            cls = type(item).__name__
            obj_cls = cls.replace('Tag', '') if cls.endswith('Tag') else cls
            if obj_cls not in out_dict['objects']:
                out_dict['objects'][obj_cls] = []
                out_dict['tags'][obj_cls] = {}

            if cls.endswith('Tag'):
                objid = str(item.parent)
                if objid not in out_dict['tags'][obj_cls]:
                    out_dict['tags'][obj_cls][objid] = []
                out_dict['tags'][obj_cls][objid].append(item)
            else:
                out_dict['objects'][obj_cls].append(item)

        # need set the 'import_tags' attribute of each imported item
        for obj_class in out_dict['objects']:
            objects = out_dict['objects'][obj_class]
            tags = out_dict['tags'][obj_class]
            for obj in objects:
                obj.import_tags = tags[str(obj)] if str(obj) in tags else []

        # return dict to be added to the context
        return {'sample_list': out_dict['objects']['Sample'],
                'sample_list_title': 'Samples'}


@login_required
def apply_data_import(request, pk):
    # get object
    obj = get_object_or_404(models.DataImport, pk=pk)
    url = reverse_lazy("pylims:data_import_detail", kwargs={'pk': pk})

    try:
        # try to apply import
        result = obj.apply_import(save=True)
        message = "Imported %s objects" % len(result)
        # on success, redirect to the import detail page
        return redirect(url + "?" + urlencode({'apply_success': message}))
    except Exception as e:
        # on fail, redirect to the import detail page and indicate failure
        return redirect(url + "?" + urlencode({'apply_error': str(e)}))
