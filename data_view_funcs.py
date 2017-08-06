
import re
from django.forms import fields as all_fields
from django.forms.models import fields_for_model

FIELDS = {}
for name in dir(all_fields):
    obj = getattr(all_fields, name)
    try:
        if issubclass(obj, all_fields.Field):
            FIELDS[name] = obj
    except TypeError:
        pass
DEFAULT_FIELD = all_fields.TextInput()


def as_field(obj):
    """
    Make an object of type field
    :param obj: An object
    :return: A Field instance or a raised TypeError
    """
    if isinstance(obj, all_fields.Field):
        # Field instances are returned as is
        return obj
    elif issubclass(obj, all_fields.Field):
        # Field types are instantiated with no arguments
        return obj()
    elif isinstance(obj, str) and (obj in FIELDS):
        # string class names are returned as instances
        return FIELDS[obj]()
    elif isinstance(obj, dict) and ("class" in obj) and ("kwargs" in obj) \
            and (obj["class"] in FIELDS) and isinstance(obj["kwargs"], dict):
        # a dict {"class": "ClassName", "kwargs": {}} can be used
        # to create a field
        return FIELDS[obj["class"]](**obj["kwargs"])
    else:
        raise TypeError("%s could not be coerced to type Field" % obj)


def list_fields(model):
    """
    Lists fields and field classes from a model.
    :param model: A django model
    :return: A dict with a name: class mapping
    """
    return {name: field for name, field in fields_for_model(model).items()}


def parse_column_spec(spec):
    """
    Parse a column specification, in the form *::*
    :param spec: A column specification
    :return: A 2-tuple of the parsed specification
    """
    column_spec_re = re.compile(r"^(.*?)::(.+)$")
    return column_spec_re.match(spec).groups()
