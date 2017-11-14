import json
import re
import datetime
from django.db import models
from django.core import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify


def pretty_json(obj):
    jsstr = serializers.serialize("json", [obj, ])
    return json.dumps(json.loads(jsstr)[0], indent=4)


class TagsField(models.TextField):
    """
    This custom field is only valid if the text is valid JSON
    """

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        super(TagsField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Make sure value is valid JSON or '' or None"""
        if value:
            try:
                json.loads(value)
                return value
            except ValueError as e:
                raise ValidationError("Invalid JSON: %s" % e)
        else:
            return value


class Project(models.Model):
    name = models.CharField(max_length=55, unique=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
    created = models.DateTimeField("created", auto_now_add=True)
    modified = models.DateTimeField("modified", auto_now=True)

    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Project, self).save(*args, **kwargs)

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.name


class ProjectTag(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    key = models.SlugField(max_length=55)
    value = models.TextField(blank=False)

    def save(self, *args, **kwargs):
        # update parent param modified tag
        self.project.modified = datetime.datetime.now()
        super(ProjectTag, self).save(*args, **kwargs)

    def __str__(self):
        return '%s="%s"' %(self.key, self.value)


class Location(models.Model):
    name = models.CharField(max_length=55, unique=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
    created = models.DateTimeField("created", auto_now_add=True)
    modified = models.DateTimeField("modified", auto_now=True)

    description = models.TextField(blank=True)
    geometry = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.name


class LocationTag(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    key = models.SlugField(max_length=55)
    value = models.TextField(blank=False)

    def save(self, *args, **kwargs):
        # update parent param modified tag
        self.location.modified = datetime.datetime.now()
        super(LocationTag, self).save(*args, **kwargs)

    def __str__(self):
        return '%s="%s"' %(self.key, self.value)


class Sample(models.Model):
    name = models.CharField(max_length=25, blank=True)
    slug = models.CharField(max_length=55, unique=True, editable=False)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
    created = models.DateTimeField("created", auto_now_add=True)
    modified = models.DateTimeField("modified", auto_now=True)

    collected = models.DateTimeField("collected", blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.set_slug()
        super(Sample, self).save(*args, **kwargs)

    def set_slug(self):
        dt = self.collected if self.collected else self.created if self.created else datetime.datetime.now()
        location_slug = self.location.slug[:10] if self.location else ""
        user = self.user.username if self.user else ""
        hint = slugify(self.name)

        for date_fun in [self.short_date, self.long_date, self.longest_date]:
            dt_str = date_fun(dt)
            id_str = "_".join(item for item in [user, dt_str, location_slug, hint] if item)
            id_str = id_str[:55]
            other_objects = Sample.objects.filter(slug = id_str)
            if len(other_objects) == 0:
                self.slug = id_str
                return

        self.slug = str(self.pk)

    def short_date(self, dt):
        return str(dt.date())

    def long_date(self, dt):
        return "%sT%s.%s.%s" % (dt.date(), dt.hour, dt.minute, dt.second)

    def longest_date(self, dt):
        return ("%sT%s" % (dt.date(), dt.time())).replace(":", ".")

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.slug


class SampleTag(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    key = models.SlugField(max_length=55)
    value = models.TextField(blank=False)

    def save(self, *args, **kwargs):
        # update parent param modified tag
        self.sample.modified = datetime.datetime.now()
        super(SampleTag, self).save(*args, **kwargs)

    def __str__(self):
        return '%s="%s"' %(self.key, self.value)


class Parameter(models.Model):
    name = models.CharField(max_length=55, unique=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    created = models.DateTimeField("created", auto_now_add=True)
    modified = models.DateTimeField("modified", auto_now=True)

    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Parameter, self).save(*args, **kwargs)

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.slug if self.slug else self.name


class ParameterTag(models.Model):
    param = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    key = models.SlugField(max_length=55)
    value = models.TextField(blank=False)

    def save(self, *args, **kwargs):
        # update parent param modified tag
        self.param.modified = datetime.datetime.now()
        super(ParameterTag, self).save(*args, **kwargs)

    def __str__(self):
        return '%s="%s"' %(self.key, self.value)


class Measurement(models.Model):
    param = models.ForeignKey(Parameter, on_delete=models.PROTECT)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)
    tags = TagsField()

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
    created = models.DateTimeField("created", auto_now_add=True)
    modified = models.DateTimeField("modified", auto_now=True)

    def parse_tags(self):
        return json.load(self.tags)

    def set_tags(self, **kwargs):
        tags_dict = self.parse_tags()
        for key, value in kwargs.items():
            tags_dict[key] = value
        self.tags = json.dumps(tags_dict)

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        if self.tags:
            str_out = "%s = %s %s" % (self.param, self.value, self.tags)
            # limit output to 150 chars or so
            if len(str_out) > 147:
                return str_out[:147] + "..."
            else:
                return str_out
        else:
            return "%s = %s" % (self.param, self.value)
