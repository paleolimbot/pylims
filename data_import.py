
import csv

from django.forms.models import fields_for_model


# keep a dictionary of importers that can be registered
_IMPORTERS = {}


# function to register import functions that can be resolved using
# resolve_importer
def register_importer(import_function, name=None, app=None):
    global _IMPORTERS
    app = str(app) if app else None
    if not name:
        raise ValueError("Import functions must have an app and name argument")
    name = str(name)

    if not callable(import_function):
        raise ValueError("Import function is not callable")

    if app not in _IMPORTERS:
        _IMPORTERS[app] = {}
    _IMPORTERS[app][name] = import_function


# decorator to register an import function
class pylims_importer(object):
    def __init__(self, app=None, name=None):
        self.name = name
        self.app = app

    def __call__(self, f):
        if self.name is None:
            self.name = f.__name__
        register_importer(f, self.name, self.app)
        return f


# does the opposite of register_importer, returning None silently if importer is not found
def resolve_function(importer_name):
    global _IMPORTERS
    if not importer_name:
        return None

    importer_split = importer_name.split(".", maxsplit=1)
    if len(importer_split) == 2:
        app, name = importer_split
    else:
        app = None
        name = importer_split[0]

    if app in _IMPORTERS and name in _IMPORTERS[app]:
        return _IMPORTERS[app][name]

    return None


def list_fields(model):
    """
    Lists fields and field classes from a model.
    :param model: A django model
    :return: A dict with a name: class mapping
    """
    return {name: field for name, field in fields_for_model(model).items()}


def _resolve_object(model, field, value, models):
    # turn model into a model class name
    model_class_name = model.replace('_', ' ').title().replace(' ', '')
    if model_class_name not in models:
        raise ValueError("Model class for %s was not provided to the import function" % model_class_name)
    model_class = models[model_class_name]
    query_args = {field: value}
    return model_class.objects.get(**query_args)


def _row_as_model(row_model_obj, row_model_tag_obj, row, models, **kwargs):
    """
    This function turns a dictionary like {'name'='my sample name'}
    into a Sample(name='my sample id')
    """
    fields = list_fields(row_model_obj)
    obj = row_model_obj()
    tags = []
    for key, value in row.items():
        if '.' in key:
            model_slug, lookup_field = key.split('.', maxsplit=1)
            if model_slug not in fields:
                raise ValueError("%s is not a field in %s" % (model_slug, row_model_obj.__name__))
            # if value is blank, don't try to resolve it
            if not value:
                continue
            target_object = _resolve_object(model_slug, lookup_field, value, models)
            setattr(obj, model_slug, target_object)

        else:
            if key in fields:
                setattr(obj, key, value)
            else:
                tag = row_model_tag_obj(parent=obj, key=key, value=value)
                tags.append(tag)

    return [obj, ] + tags


def _table_import(header, row_generator, models, row_model, **kwargs):
    row_model_obj = models[row_model]
    row_model_tag_obj = models[row_model + "Tag"]

    final_models = []
    for row in row_generator():
        if row:
            # zip with headers to make dictionary for the row
            row_dict = {key: value for key, value in zip(header, row)}

            # get model from the row
            models_for_row = _row_as_model(row_model_obj, row_model_tag_obj,
                                          row_dict, models, **kwargs)
            if models_for_row:
                for obj in models_for_row:
                    final_models.append(obj)

    return final_models


@pylims_importer()
def csv_import(text, models, row_model="Sample", **kwargs):

    if not text:
        raise ValueError("Value 'text' is empty")

    csv_reader = csv.reader(text.splitlines())
    csv_iter = iter(csv_reader)
    header = list(next(csv_reader))

    def row_generator():
        line = next(csv_iter, None)
        while line is not None:
            yield line
            line = next(csv_iter, None)

    return _table_import(header, row_generator, models, row_model, **kwargs)
