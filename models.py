import json
import re
import datetime
from django.db import models
from django.core import serializers
from django.contrib.auth.models import User


def pretty_json(obj):
    jsstr = serializers.serialize("json", [obj, ])
    return json.dumps(json.loads(jsstr)[0], indent=4)


class Project(models.Model):
    name = models.CharField(max_length=55, unique=True)
    description = models.TextField()
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
    created = models.DateTimeField("created", auto_now_add=True)

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=55, unique=True)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
    created = models.DateTimeField("created", auto_now_add=True)
    description = models.TextField(blank=True)
    geometry = models.TextField(blank=True)

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.name


class Sample(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
    created = models.DateTimeField("created", auto_now_add=True)
    user_id = models.CharField(max_length=25, blank=True)
    sample_id = models.CharField(max_length=55, editable=False)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, blank=True, null=True)
    collected = models.DateTimeField("collected", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.set_sample_id()
        super(Sample, self).save(*args, **kwargs)

    def set_sample_id(self):
        dt = self.collected if self.collected else self.created if self.created else datetime.datetime.now()
        location_slug = re.compile(r'[^a-z0-9]+').sub("-",  self.location.name.lower())[:5] if self.location else ""
        user = self.user_created.username if self.user_created else ""
        hint = re.compile(r'[^a-z0-9]+').sub("-", self.user_id.strip().lower())

        for date_fun in [self.short_date, self.long_date, self.longest_date]:
            dt_str = date_fun(dt)
            id_str = "/".join(item for item in [user, dt_str, location_slug, hint] if item)
            other_objects = Sample.objects.filter(sample_id = id_str)
            if len(other_objects) == 0:
                self.sample_id = id_str
                return

        self.sample_id = str(self.pk)

    def short_date(self, dt):
        return str(dt.date())

    def long_date(self, dt):
        return "%sT%s:%s:%s" % (dt.date(), dt.hour, dt.minute, dt.second)

    def longest_date(self, dt):
        return "%sT%s" % (dt.date(), dt.time())

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.sample_id


class SampleTag(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    key = models.CharField(max_length=55)
    value = models.TextField(blank=False)


class Parameter(models.Model):
    name = models.CharField(max_length=55, unique=True)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    created = models.DateTimeField("created", auto_now_add=True)
    short_name = models.CharField(max_length=55, blank=True, unique=True, null=True)
    description = models.TextField(blank=True)

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.short_name if self.short_name else self.name


class Measurement(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    created = models.DateTimeField("created", auto_now_add=True)
    param = models.ForeignKey(Parameter, on_delete=models.PROTECT)
    value = models.TextField(blank=True, null=True)

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return "%s = %s" % (self.param, self.value)


class MeasurementTag(models.Model):
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    key = models.CharField(max_length=55)
    value = models.TextField(blank=False)

    def as_json(self):
        return pretty_json(self)