import json
import re
from django.db import models
from django import forms
from django.core import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


def pretty_json(obj):
    jsstr = serializers.serialize("json", [obj, ])
    return json.dumps(json.loads(jsstr)[0], indent=4)


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
        if self:
            return json.dumps(self)
        else:
            return ""

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, dict):
            return dict(self) == dict(other)
        elif isinstance(other, str):
            if not bool(self) and not bool(other):
                return True
            try:
                return dict(self) == json.loads(other)
            except ValueError:
                return False
        else:
            try:
                return not bool(self) and not bool(other)
            except:
                return False

    def __ne__(self, other):
        return not self.__eq__(other)


class TagsField(models.TextField):
    """
    This custom field handles converting data from a dict to a json and back
    """

    def __init__(self, *args, **kwargs):
        kwargs['default'] = '{}'
        kwargs['blank'] = True
        kwargs['null'] = False
        super(TagsField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return JSONDict()
        elif value == '':
            return JSONDict()
        else:
            return JSONDict(**json.loads(value))

    def to_python(self, value):
        if value is None:
            return JSONDict()
        elif value == '':
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
            return ""
        elif isinstance(value, dict) and (len(value) == 0):
            return ""
        elif isinstance(value, dict):
            return json.dumps(value)
        elif isinstance(value, str):
            return value
        else:
            raise ValidationError('Object of type "%(objtype)s" could not be converted to a dict',
                                  params={'objtype': type(value).__name__}, code='invalid')

    def deconstruct(self):
        name, path, args, kwargs = super(TagsField, self).deconstruct()
        if 'default' in kwargs:
            del kwargs['default']
        if 'blank' in kwargs:
            del kwargs['blank']
        if 'null' in kwargs:
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
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    created = models.DateTimeField("created", auto_now_add=True)
    tags = TagsField()

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=55, unique=True)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    created = models.DateTimeField("created", auto_now_add=True)
    description = models.TextField(blank=True)
    geometry = models.TextField(blank=True)
    tags = TagsField()

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.name


class Sample(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    created = models.DateTimeField("created", auto_now_add=True)
    sample_id = models.CharField(max_length=55, unique=True, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, blank=True, null=True)
    collected = models.DateTimeField("collected", blank=True, null=True)
    comment = models.TextField(blank=True)
    tags = TagsField()

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.sample_id


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


class Unit(models.Model):
    name = models.CharField(max_length=55, unique=True)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    created = models.DateTimeField("created", auto_now_add=True)
    short_name = models.CharField(max_length=55, blank=True, unique=True, null=True)
    description = models.TextField(blank=True)

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return self.short_name if self.short_name else self.name


class SampleMeta(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    created = models.DateTimeField("created", auto_now_add=True)
    param = models.ForeignKey(Parameter, on_delete=models.PROTECT)
    value = models.FloatField(blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, blank=True, null=True)
    RDL = models.FloatField(blank=True, null=True)
    non_detect = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    tags = TagsField()

    def as_json(self):
        return pretty_json(self)

    def __str__(self):
        return "%s = %s" % (self.param, self.value)


class DataView(models.Model):
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    created = models.DateTimeField("created", auto_now_add=True)
    mapping = TagsField()

    def parse_column_spec(self, spec):
        column_spec_re = re.compile(r"^(.+?)\.(.+)$")
        obj, attr = column_spec_re.match(spec).groups()
        if obj == "sample":
            if attr in ("sample_id", "comment", "location", "collected"):
                def f(sample):
                    return getattr(sample, attr)
            else:
                def f(sample):
                    return sample.tags[attr] if attr in sample.tags else None
        else:
            def f(sample):
                params = Parameter.objects.filter(short_name=obj)
                if params:
                    metas = SampleMeta.objects.filter(sample=sample, param=params[0])
                    if attr in ("created", "value", "unit", "RDL", "non_detect", "comment"):
                        return {meta.pk: getattr(meta, attr) for meta in metas}
                    else:
                        return {meta.pk: meta.tags[attr] if attr in meta.tags else None for meta in metas}
                else:
                    raise ValueError("No such parameter: %s" % obj)
        return f

    def render_table(self, samples):
        funcs = [self.parse_column_spec(col) for col in self.mapping["columns"]]
        data = [[func(sample) for func in funcs] for sample in samples]
        return data
