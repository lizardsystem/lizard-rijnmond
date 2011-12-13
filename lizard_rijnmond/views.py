# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_rijnmond.models import Measure
from lizard_rijnmond.models import Scenario
from lizard_rijnmond.models import Year
from lizard_rijnmond.models import Strategy
from lizard_rijnmond.models import RiverlineResult

logger = logging.getLogger(__name__)


def segment_map(request, template="lizard_rijnmond/segment_map.html"):
    measures = Measure.objects.all()

    return render_to_response(
        template,
        {'measures': measures,
         },
        context_instance=RequestContext(request))


def water_level_map(request, template="lizard_rijnmond/water_level_map.html"):
    strategy_id = request.GET.get('strategy_id')
    scenario_id = request.GET.get('scenario_id')
    year_id = request.GET.get('year_id')
    scenarios = Scenario.objects.all()
    years = Year.objects.all()
    strategies = Strategy.objects.all()
    if strategy_id and scenario_id and year_id:
        logger.debug("Filtering riverline_results")
        results = RiverlineResult.objects.filter(
            strategy=int(strategy_id),
            scenario=int(scenario_id),
            year=int(year_id))
    else:
        results = []
    return render_to_response(
        template,
        {'scenarios': scenarios,
         'years': years,
         'strategies': strategies,
         'results': results,
         'scenario_id': scenario_id,
         'strategy_id': strategy_id,
         'year_id': year_id,
         },
        context_instance=RequestContext(request))
