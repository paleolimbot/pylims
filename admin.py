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
class ProjectMetaInline(admin.TabularInline):
    model = models.ProjectMeta
    formfield_overrides = text_overrides


class ProjectAdmin(VersionAdmin):
    inlines = [ProjectMetaInline]
    formfield_overrides = text_overrides


class LocationMetaInline(admin.TabularInline):
    model = models.LocationMeta
    formfield_overrides = text_overrides


class LocationAdmin(VersionAdmin):
    inlines = [LocationMetaInline]
    formfield_overrides = text_overrides


class SampleMetaInline(admin.TabularInline):
    model = models.SampleMeta
    formfield_overrides = text_overrides


class SampleAdmin(VersionAdmin):
    inlines = [SampleMetaInline]
    formfield_overrides = text_overrides


class SampleMetaKeyAdmin(VersionAdmin):
    formfield_overrides = text_overrides


class UnitAdmin(VersionAdmin):
    formfield_overrides = text_overrides

# register models with the admin site
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Sample, SampleAdmin)
admin.site.register(models.SampleMetaKey, SampleMetaKeyAdmin)
admin.site.register(models.Unit, UnitAdmin)
