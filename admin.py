from django.contrib import admin
from . import models

# setup inlines


class ProjectMetaInline(admin.TabularInline):
    model = models.ProjectMeta

class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectMetaInline]

class LocationMetaInline(admin.TabularInline):
    model = models.LocationMeta

class LocationAdmin(admin.ModelAdmin):
    inlines = [LocationMetaInline]

class SampleMetaInline(admin.TabularInline):
    model = models.SampleMeta

class SampleAdmin(admin.ModelAdmin):
    inlines = [SampleMetaInline]


admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Sample, SampleAdmin)
admin.site.register(models.SampleMetaKey)
