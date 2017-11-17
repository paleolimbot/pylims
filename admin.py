from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea
from reversion.admin import VersionAdmin

from . import models

# This text override gets used in all models to keep the size down
text_overrides = {
    TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 40})},
}


# define base class that all models inherit
class PylimsAdmin(VersionAdmin):
    formfield_overrides = text_overrides

    def save_model(self, request, obj, form, change):
        # save created user from admin login
        if obj.user is None:
            obj.user = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        if formset.model == models.Measurement:
            instances = formset.save(commit=False)
            for instance in instances:
                # save created user from admin site
                if instance.user is None:
                    instance.user = request.user
                instance.save()
        else:
            formset.save()


# setup inline admins
class ProjectTagInline(admin.TabularInline):
    model = models.ProjectTag
    formfield_overrides = text_overrides
    extra = 1


class LocationTagInline(admin.TabularInline):
    model = models.LocationTag
    formfield_overrides = text_overrides
    extra = 1


class SampleTagInline(admin.TabularInline):
    model = models.SampleTag
    formfield_overrides = text_overrides
    extra = 1


class MeasurementInline(admin.TabularInline):
    model = models.Measurement
    formfield_overrides = text_overrides
    extra = 1


class ParameterTagInline(admin.TabularInline):
    model = models.ParameterTag
    formfield_overrides = text_overrides
    extra = 1


# setup admins
class ProjectAdmin(PylimsAdmin):
    inlines = [ProjectTagInline, ]
    prepopulated_fields = {"slug": ("name",)}
    change_list_template = "admin/pylims/project/change_list.html"
    change_form_template = "admin/pylims/project/change_form.html"


class LocationAdmin(PylimsAdmin):
    inlines = [LocationTagInline, ]
    prepopulated_fields = {"slug": ("name",)}
    change_list_template = "admin/pylims/location/change_list.html"
    change_form_template = "admin/pylims/location/change_form.html"


class SampleAdmin(PylimsAdmin):
    inlines = [SampleTagInline, MeasurementInline]
    change_list_template = "admin/pylims/sample/change_list.html"
    change_form_template = "admin/pylims/sample/change_form.html"


class ParameterAdmin(PylimsAdmin):
    inlines = [ParameterTagInline, ]
    prepopulated_fields = {"slug": ("name",)}
    change_list_template = "admin/pylims/parameter/change_list.html"
    change_form_template = "admin/pylims/parameter/change_form.html"

class DataImportAdmin(PylimsAdmin):
    pass

# register models with the admin site
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Sample, SampleAdmin)
admin.site.register(models.Parameter, ParameterAdmin)
admin.site.register(models.DataImportDriver)
admin.site.register(models.DataImport, DataImportAdmin)
