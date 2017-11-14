
import re

TAG_QUERY_KEY = re.compile(r"^tag_(.*)$")


def filter_sample_table(queryset, q):
    """
    Consistent filtering, ordering of sample tables based on query params:
    
    Date/times:
    created_start = The first allowed creation date/time, YYYY-MM-DDThh:mm:ssZ
    created_end = The last allowed creation date/time, YYYY-MM-DDThh:mm:ssZ
    collected_start = The first allowed collection date/time, YYYY-MM-DDThh:mm:ssZ
    collected_end = The last allowed collection date/time, YYYY-MM-DDThh:mm:ssZ
    modified_start = The first allowed modified date/time, YYYY-MM-DDThh:mm:ssZ
    modified_end = The last allowed modified date/time, YYYY-MM-DDThh:mm:ssZ
    
    Projects:
    project_slug = value (matches project slug)
    project_id = value (matches project ID)
    
    Locations:
    location_slug = value (matches location slug)
    location_id = value (matches location ID)
    
    Parent samples:
    sample_slug = value (matches parent sample slug)
    sample_id = value (matches parent sample ID)
    
    Has measurement with parameter:
    param_slug = value (has at least one measurement with param matching slug)
    param_id = value (has at least one measurement with param matching id)
    
    Tags:
    tag_* = "" (tag * not defined), = "__exists__" (tag * is defined), = value (tag = value)
    
    Pagination and ordering
    n_samples = number of results to show on a page (>1)
    paged = number of pages in (>1)
    order_by = values passed to QuerySet.order_by()
    
    
    :param queryset: The quereyset of samples to filter
    :param request: The request with a GET attribute
    :return: A dictionary with additional context variables for the sample_table.html template
    """

    # Date/times:
    if q.get("created_start"):
        queryset = queryset.filter(created__gte=q["created_start"])

    if q.get("collected_start"):
        queryset = queryset.filter(collected__gte=q["collected_start"])

    if q.get("modified_start"):
        queryset = queryset.filter(modified__gte=q["modified_start"])

    if q.get("created_end"):
        queryset = queryset.filter(created__lte=q["created_end"])

    if q.get("collected_end"):
        queryset = queryset.filter(collected__lte=q["collected_end"])

    if q.get("modified_end"):
        queryset = queryset.filter(modified__lte=q["modified_end"])

    # Projects (can pass multiple IDs/slugs
    project_slugs = q.getlist("project_slug")
    if project_slugs:
        queryset = queryset.filter(project__slug__in=project_slugs)
    project_ids = q.getlist("project_id")
    if project_ids:
        queryset = queryset.filter(project__id__in=project_ids)

    # Locations (can pass multiple IDs/slugs
    location_slugs = q.getlist("location_slug")
    if location_slugs:
        queryset = queryset.filter(location__slug__in=location_slugs)
    location_ids = q.getlist("location_id")
    if location_ids:
        queryset = queryset.filter(location__id__in=location_ids)

    # Parent samples (can pass multiple IDs/slugs
    sample_slugs = q.getlist("sample_slug")
    if sample_slugs:
        queryset = queryset.filter(parent__slug__in=sample_slugs)
    sample_ids = q.getlist("sample_id")
    if sample_ids:
        queryset = queryset.filter(parent__id__in=sample_ids)

    # Has measurement with parameter (can pass multiple IDs/slugs)
    param_slugs = q.getlist("param_slug")
    if param_slugs:
        queryset = queryset.filter(measurement__param__slug__in=param_slugs)
    param_ids = q.getlist("param_id")
    if param_ids:
        queryset = queryset.filter(measurement__param__id__in=param_ids)

    # Tags (can pass query param as anything like tag_*)
    tag_keys = [key for key in q if TAG_QUERY_KEY.match(key)]
    for tag_key in tag_keys:
        tag = TAG_QUERY_KEY.match(tag_key).group(1)
        values = q.getlist(tag_key)
        # if any value is '__exists__', just filter anything that has that tag
        if any(value == "__exists__" for value in values):
            queryset = queryset.filter(sampletag__key=tag)
        elif any(value == "" for value in values):
            queryset = queryset.exclude(sampletag__key=tag)
        else:
            queryset = queryset.filter(sampletag__key=tag, sampletag__value__in=values)

    # Ordering
    order_by = q.getlist("order_by", ['-modified'])
    if order_by:
        queryset = queryset.order_by(*order_by)

    # Pagination
    n_results_int = int(q.get("n_samples", "100"))
    paged_int = int(q.get("paged", "1"))

    n_results = max(n_results_int, 1)  # make sure n_results is never negative
    paged = max(paged_int, 1)  # make sure paged is never negative
    start = n_results * (paged - 1)
    end = n_results * paged
    queryset = queryset[start:end]

    # return the sample list and the query
    return {"sample_list": queryset, "query": q}
