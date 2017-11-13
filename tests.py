from django.test import TestCase
from .models import *
import numpy as np


def create_base_data():
    # create a project, two locations, and two parameters
    proj = Project(name="fish")
    proj.save()

    loc1 = Location(name="location1")
    loc1.save()

    loc2 = Location(name="location2")
    loc2.save()

    pH = Parameter(name="pH")
    pH.save()

    alk = Parameter(name="Alkalinity", slug="alk")
    alk.save()

    # create some samples and some random data
    samples = [Sample(project=proj, name="Sample %d" % n) for n in range(5)]
    for sample in samples:
        sample.save()
        for param in (pH, alk):
            meta = Measurement(sample=sample, param=param, value=np.random.uniform())
            meta.save()
