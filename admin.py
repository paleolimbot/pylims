from django.contrib import admin
from django.db.models import TextField
from django.forms import ModelForm, Textarea

from . import models
from django.forms.widgets import TextInput


text_overrides = {
    TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 40})},
}

# setup inline admins
class ProjectMetaInline(admin.TabularInline):
    model = models.ProjectMeta
    formfield_overrides = text_overrides


class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectMetaInline]
    formfield_overrides = text_overrides


class LocationMetaInline(admin.TabularInline):
    model = models.LocationMeta
    formfield_overrides = text_overrides


class LocationAdmin(admin.ModelAdmin):
    inlines = [LocationMetaInline]
    formfield_overrides = text_overrides


class SampleMetaInline(admin.TabularInline):
    model = models.SampleMeta
    formfield_overrides = text_overrides


class SampleAdmin(admin.ModelAdmin):
    inlines = [SampleMetaInline]
    formfield_overrides = text_overrides


admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Sample, SampleAdmin)
admin.site.register(models.SampleMetaKey)
admin.site.register(models.Unit)
