
from django.db import models
from django.forms import Form, formset_factory
from .models import Parameter, Sample, SampleMeta, Project, Unit, Location
from .data_view_funcs import as_field, parse_column_spec, list_fields, DEFAULT_FIELD

# create a dict so that models can be passed as strings to DataView()
MODELS = {
    "Parameter": Parameter,
    "SampleMeta": SampleMeta,
    "Sample": Sample,
    "Project": Project,
    "Unit": Unit,
    "Location": Location
}


def as_model(obj):
    """
    Make an object of type model
    :param obj: An object
    :return: A model class
    """
    if issubclass(obj, models.Model):
        return obj
    elif isinstance(obj, str) and (obj in MODELS):
        return MODELS[obj]
    else:
        raise TypeError("%s could not be coerced to type Model" % obj)


class DataViewForm(Form):

    def __init__(self, data_view, *args, **kwargs):
        super(DataViewForm, self).__init__(*args, **kwargs)
        for item in data_view.column_spec:
            self.fields[item] = data_view.fields[item]


class DataView:
    """
    A DataView is a method to get the non-flat model/tags structure
    into a flat table for viewing, plotting, and data entry
    """

    def __init__(self, model, spec, fields=None):
        """
        Create a DataView with a model, column specification, and fields
        :param model: A django model
        :param spec: A list of column specs
        :param fields: A dictionary with the key as a column spec and a value as a field
        """
        self.model = as_model(model)

        # validate colspecs
        if not spec:
            raise ValueError("spec must have len > 0")
        self.column_spec = spec
        self.columns = [parse_column_spec(colspec) for colspec in spec]

        # validate fields
        if fields is None:
            fields = {}
        model_fields = list_fields(self.model)
        self.fields = {}
        for item in self.column_spec:
            obj, attr = parse_column_spec(item)
            if obj == "" and attr in model_fields:
                self.fields[item] = model_fields[attr]
            elif item in fields:
                self.fields[item] = as_field(fields[item])
            else:
                self.fields[item] = DEFAULT_FIELD

    def data_iter(self):
        pass

    def as_form(self, *args, **kwargs):
        return DataViewForm(self, *args, **kwargs)

    def _as_formset_base(self, *args, **kwargs):
        return formset_factory(self.as_form, *args, **kwargs)

    def as_formset(self, *args, extra=1, can_order=False, can_delete=False, max_num=None,
                   validate_max=False, min_num=None, validate_min=False, **kwargs):
        return self._as_formset_base(extra=extra, can_order=can_order, can_delete=can_delete,
                                     max_num=max_num, validate_max=validate_max, min_num=min_num,
                                     validate_min=validate_min)(*args, **kwargs)


class SampleDataView(DataView):
    """
    Samples are a little different in that they have a two-part specification,
    with the first part being the short_name of the Parameter, and the second
    part being the field spec as above.
    """

    def __init__(self, spec, fields=None):
        super(SampleDataView, self).__init__(Sample, spec, fields)

        # dealing with meta fields
        meta_fields = list_fields(SampleMeta)

        # need to reassign two-part specifications and check
        # parameter names
        self.params = {}
        for item in self.column_spec:
            obj, attr = parse_column_spec(item)
            if obj != "":
                param = Parameter.objects.filter(short_name=obj)
                if not param:
                    raise ValueError("Parameter `%s` was not found" % obj)
                self.params[item] = param[0]
            if obj != "" and attr in meta_fields:
                self.fields[item] = meta_fields[attr]
