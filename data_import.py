import csv

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


def _row_as_model(row_model_obj, row_model_tag_obj, row, models, **kwargs):
    """
    This function turns a dictionary like {'name'='my sample name'}
    into a Sample(name='my sample id')
    """

    print("row_import with row: %s" % row)
    return []


def _table_import(header, row_generator, models, row_model, **kwargs):
    row_model_obj = models[row_model]
    row_model_tag_obj = models[row_model + "Tag"]

    final_models = []
    for row in row_generator():
        if row:
            # zip with headers to make dictionary for the row
            row_dict = {key: value for key, value in zip(header, row)}

            # get model from the row
            model_for_row = _row_as_model(row_model_obj, row_model_tag_obj,
                                          row_dict, models, **kwargs)
            if model_for_row:
                final_models.append(model_for_row)

    return final_models


@pylims_importer()
def csv_import(file, models, row_model="Sample", **kwargs):

    with open(file.file.name, newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        csv_iter = iter(csv_reader)
        header = list(next(csv_reader))

        def row_generator():
            line = next(csv_iter, None)
            while line is not None:
                yield line
                line = next(csv_iter, None)

        return _table_import(header, row_generator, models, row_model, **kwargs)
