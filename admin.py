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
        if obj.user_created is None:
            obj.user_created = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        if formset.model == models.SampleMeta:
            instances = formset.save(commit=False)
            for instance in instances:
                # save created user from admin site
                if instance.user_created is None:
                    instance.user_created = request.user
                instance.save()
        else:
            formset.save()


# setup inline admins
class ProjectAdmin(PylimsAdmin):
    pass


class LocationAdmin(PylimsAdmin):
    pass


class SampleMetaInline(admin.TabularInline):
    model = models.SampleMeta
    formfield_overrides = text_overrides


class SampleAdmin(PylimsAdmin):
    inlines = [SampleMetaInline]


class ParameterAdmin(PylimsAdmin):
    pass


class UnitAdmin(PylimsAdmin):
    pass


class DataViewAdmin(PylimsAdmin):
    pass

# register models with the admin site
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Sample, SampleAdmin)
admin.site.register(models.Parameter, ParameterAdmin)
admin.site.register(models.Unit, UnitAdmin)
admin.site.register(models.DataView, DataViewAdmin)
