# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_rijnmond.models import Measure


def segment_map(request, template="lizard_rijnmond/segment_map.html"):
    measures = Measure.objects.all()

    return render_to_response(
        template,
        {'measures': measures,
         },
        context_instance=RequestContext(request))
