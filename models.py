import json
from django.db import models
from django import forms
from django.core import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class JSONDict(dict):
    """
    This is a custom dict that simply replaces the __str__ method with a JSON
    string instead of a dict string. This is because the default admin panel uses
    the __str__ method of the field by default, and a using a regular dict causes
    JSON syntax errors when these objects are modified.
    """

    def __init__(self, **kwargs):
        super(JSONDict, self).__init__(**kwargs)

    def __str__(self):
        return json.dumps(self)


class TagsField(models.TextField):
    """
    This custom field handles converting data from a dict to a json and back
    """

    def __init__(self, *args, **kwargs):
        kwargs['default'] = '{}'
        kwargs['blank'] = True
        kwargs['null'] = True
        super(TagsField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return JSONDict()
        else:
            return JSONDict(**json.loads(value))

    def to_python(self, value):
        if value is None:
            return JSONDict()
        elif isinstance(value, dict):
            return JSONDict(**value)
        elif isinstance(value, str):
            try:
                return JSONDict(**json.loads(value))
            except ValueError as e:
                raise ValidationError('The value `%(value)s` could not be converted to JSON (%(error)s)',
                                      params={'value': value, 'error': str(e)}, code='invalid')
        else:
            raise ValidationError('Object of type "%(objtype)s" could not be converted to a dict',
                                  params={'objtype': type(value).__name__}, code='invalid')

    def get_prep_value(self, value):
        if value is None:
            return '{}'
        elif isinstance(value, dict):
            return json.dumps(value)
        elif isinstance(value, str):
            return value
        else:
            raise ValidationError('Object of type "%(objtype)s" could not be converted to a dict',
                                  params={'objtype': type(value).__name__}, code='invalid')

    def deconstruct(self):
        name, path, args, kwargs = super(TagsField, self).deconstruct()
        del kwargs['default']
        del kwargs['blank']
        del kwargs['null']
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': forms.CharField}
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 200
        defaults.update(kwargs)
        return super(TagsField, self).formfield(**defaults)


class Project(models.Model):
    name = models.CharField(max_length=55, unique=True)
    description = models.TextField()
    user_created = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField("created", auto_now_add=True)

    def as_json(self):
        return serializers.serialize("json", [self, ])

    def __str__(self):
        return self.name


class ProjectMeta(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    key = models.CharField(max_length=55)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField("created", auto_now_add=True)
    value = models.TextField()
    tags = TagsField()

    class Meta:
        unique_together = ('project', 'key',)

    def __str__(self):
        return "%s = %s" % (self.key, self.value)


class Location(models.Model):
    name = models.CharField(max_length=55, unique=True)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField("created", auto_now_add=True)
    description = models.TextField(blank=True)
    geometry = models.TextField(blank=True)

    def as_json(self):
        return serializers.serialize("json", [self, ])

    def __str__(self):
        return self.name


class LocationMeta(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    key = models.CharField(max_length=55, unique=True)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField("created", auto_now_add=True)
    value = models.TextField()
    tags = TagsField()

    class Meta:
        unique_together = ('location', 'key',)

    def __str__(self):
        return "%s = %s" % (self.key, self.value)


class Sample(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField("created", auto_now_add=True)
    sample_id = models.CharField(max_length=55, unique=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, blank=True, null=True)
    collected = models.DateTimeField("collected")
    comment = models.TextField(blank=True)
    tags = TagsField()

    def as_json(self):
        return serializers.serialize("json", [self, ])

    def __str__(self):
        return self.sample_id


class SampleMetaKey(models.Model):
    name = models.CharField(max_length=55, unique=True)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField("created", auto_now_add=True)
    short_name = models.CharField(max_length=55, blank=True, unique=True)
    description = models.TextField(blank=True)

    def as_json(self):
        return serializers.serialize("json", [self, ])

    def __str__(self):
        return self.short_name if self.short_name else self.name


class Unit(models.Model):
    name = models.CharField(max_length=55, unique=True)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField("created", auto_now_add=True)
    short_name = models.CharField(max_length=55, blank=True, unique=True)
    description = models.TextField(blank=True)

    def as_json(self):
        return serializers.serialize("json", [self, ])

    def __str__(self):
        return self.short_name if self.short_name else self.name


class SampleMeta(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField("created", auto_now_add=True)
    key = models.ForeignKey(SampleMetaKey, on_delete=models.PROTECT)
    value = models.FloatField(blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, blank=True, null=True)
    RDL = models.FloatField(blank=True, null=True)
    non_detect = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    tags = TagsField()

    def as_json(self):
        return serializers.serialize("json", [self, ])

    def __str__(self):
        return "%s = %s" % (self.key, self.value)
