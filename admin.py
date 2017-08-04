from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea
from reversion.admin import VersionAdmin

from . import models

# This text override gets used in all models to keep the size down
text_overrides = {
    TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 40})},
}


# setup inline admins
class ProjectAdmin(VersionAdmin):
    formfield_overrides = text_overrides


class LocationAdmin(VersionAdmin):
    formfield_overrides = text_overrides


class SampleMetaInline(admin.TabularInline):
    model = models.SampleMeta
    formfield_overrides = text_overrides


class SampleAdmin(VersionAdmin):
    inlines = [SampleMetaInline]
    formfield_overrides = text_overrides


class ParameterAdmin(VersionAdmin):
    formfield_overrides = text_overrides


class UnitAdmin(VersionAdmin):
    formfield_overrides = text_overrides


class DataViewAdmin(VersionAdmin):
    formfield_overrides = text_overrides

# register models with the admin site
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Sample, SampleAdmin)
admin.site.register(models.Parameter, ParameterAdmin)
admin.site.register(models.Unit, UnitAdmin)
admin.site.register(models.DataView, DataViewAdmin)
