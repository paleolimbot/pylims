import json
import hashlib
import datetime


from django.db import models
from django.core import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import reversion

from . import data_import


def pretty_json(obj):
    jsstr = serializers.serialize("json", [obj, ])
    return json.dumps(json.loads(jsstr)[0], indent=4)


class TagsField(models.TextField):
    """
    This custom field is only valid if the text is valid JSON
    """

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        self.type = kwargs["type"] if "type" in kwargs else None
        super(TagsField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Make sure value is valid JSON or '' or None"""
        if value:
            try:
                val = json.loads(value)
                if self.type:
                    if not isinstance(val, self.type):
                        raise ValidationError("Object is not of type %s" % self.type)
                return value
            except ValueError as e:
                raise ValidationError("Invalid JSON: %s" % e)
        else:
            return value

    @staticmethod
    def parse(value, out_type=None):
        if value:
            return json.loads(value)
        elif not value and callable(out_type):
            return out_type()
        else:
            return None


class Project(models.Model):
    name = models.CharField(max_length=55, unique=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
    created = models.DateTimeField("created", auto_now_add=True)
    modified = models.DateTimeField("modified", auto_now=True)
    data_import = models.ForeignKey('DataImport', on_delete=models.SET_NULL,
                                    null=True, blank=True, editable=False)

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
    data_import = models.ForeignKey('DataImport', on_delete=models.SET_NULL,
                                    null=True, blank=True, editable=False)

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
    data_import = models.ForeignKey('DataImport', on_delete=models.SET_NULL,
                                    null=True, blank=True, editable=False)

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
    data_import = models.ForeignKey('DataImport', on_delete=models.SET_NULL,
                                    null=True, blank=True, editable=False)

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
    data_import = models.ForeignKey('DataImport', on_delete=models.SET_NULL,
                                    null=True, blank=True, editable=False)

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
    data_import = models.ForeignKey('DataImport', on_delete=models.SET_NULL,
                                    null=True, blank=True, editable=False)

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
    data_import = models.ForeignKey('DataImport', on_delete=models.SET_NULL,
                                    null=True, blank=True, editable=False)

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
    data_import = models.ForeignKey('DataImport', on_delete=models.SET_NULL,
                                    null=True, blank=True, editable=False)

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
    data_import = models.ForeignKey('DataImport', on_delete=models.SET_NULL,
                                    null=True, blank=True, editable=False)

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


class DataImport(models.Model):
    text = models.TextField()
    applied = models.BooleanField(default=False, editable=False)
    driver = models.CharField(max_length=255, default="csv_import")
    args = TagsField()
    description = models.TextField(blank=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
    created = models.DateTimeField("created", auto_now_add=True)
    modified = models.DateTimeField("modified", auto_now=True)

    def full_clean(self, *args, **kwargs):
        super(DataImport, self).full_clean(*args, **kwargs)
        # if import is not yet applied, test running it as part of full_clean
        if not self.applied:
            self.run_import()

    def save(self, *args, **kwargs):
        # save self
        super(DataImport, self).save(*args, **kwargs)
        # if not applied, apply the import now
        self.apply_import(save=True, self_save=True)

    def run_import(self):

        # raise error if import is already applied
        if self.applied:
            raise ValidationError("This import has already been applied")

        # get args as a dict
        import_args = TagsField.parse(self.args, dict)
        # get import function
        model_objects = {
            "Project": Project,
            "ProjectTag": ProjectTag,
            "Location": Location,
            "LocationTag": LocationTag,
            "Sample": Sample,
            "SampleTag": SampleTag,
            "Parameter": Parameter,
            "ParameterTag": ParameterTag,
            "Measurement": Measurement
        }

        # get the import function
        import_fun = data_import.resolve_function(self.driver)
        if not import_fun:
            raise ValidationError("No import function could be found for driver: %s" % self.driver)
        try:
            # execute import function
            result = import_fun(self.text, models=model_objects, **import_args)

            # check for empty result
            if not result:
                raise ValidationError("Nothing to import from data")

            # check for iterable result
            if not hasattr(result, '__iter__'):
                raise ValidationError("Result was not iterable")

            # check that every item has a callable "save" method
            def valid_item(item):
                hasattr(item, "save") and callable(item.save)

            invalid_objects = [str(i) for i in range(len(result)) if not valid_item(result[i])]
            if invalid_objects:
                raise ValidationError("Invalid objects were returned at positions %s" % ", ".join(invalid_objects))

            return result
        except Exception as e:
            raise ValidationError("Import failed with %s: %s" % (type(e).__name__, e))

    def apply_import(self, save=False, self_save=False):
        """
        This applies the result (or tests the application of the result
        if save=False) to the database
        """

        # raise error if import is already applied
        if self.applied:
            raise ValidationError("This import has already been applied")

        # run the importer
        result = self.run_import()

        # save if requested
        if save:
            with reversion.create_revision():
                # Store some meta-information.
                reversion.set_user(self.user)
                reversion.set_comment("Applied data import: %s" % self)

                for item in result:
                    if hasattr(item, "user"):
                        item.user = self.user
                    if hasattr(item, "data_import"):
                        item.data_import = self
                    if save:
                        item.save()

                # set the applied flag to "True"
                self.applied = True

                # save self if requested
                if self_save:
                    self.save()

        # classify result by object type and if it currently exists or not
        out_dict = {}
        for item in result:
            cls = type(item)
            if cls not in out_dict:
                out_dict[cls] = []
            out_dict[cls].append(item)

        # return dict of added (or to-be added) objects by object type
        return out_dict

    def __str__(self):
        return "Data Import: %s" % self.created


class DataImportTag(models.Model):
    data_import = models.ForeignKey(DataImport, on_delete=models.CASCADE)
    key = models.SlugField(max_length=55)
    value = models.TextField(blank=False)
