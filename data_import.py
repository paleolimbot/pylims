import csv


def row_as_model(row_model_obj, row_model_tag_obj, row, models, **kwargs):
    """
    This function turns a dictionary like {'name'='my sample name'}
    into a Sample(name='my sample id')
    """

    print("row_import with row: %s" % row)
    return []


def table_import(header, row_generator, models, row_model, **kwargs):
    row_model_obj = models[row_model]
    row_model_tag_obj = models[row_model + "Tag"]

    final_models = []
    for row in row_generator():
        if row:
            # zip with headers to make dictionary for the row
            row_dict = {key: value for key, value in zip(header, row)}

            # get model from the row
            model_for_row = row_as_model(row_model_obj, row_model_tag_obj,
                                         row_dict, models, **kwargs)
            if model_for_row:
                final_models.append(model_for_row)

    return final_models


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

        return table_import(header, row_generator, models, row_model, **kwargs)


def resolve_function(driver_name):
    if driver_name == "csv_import":
        return csv_import

    return None
