# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging

from django.conf import settings
from lizard_map.coordinates import RD
from lizard_map.workspace import WorkspaceItemAdapter
import mapnik

from lizard_rijnmond.models import Riverline
from lizard_rijnmond.models import RiverlineResult

logger = logging.getLogger(__name__)


class SegmentAdapter(WorkspaceItemAdapter):

    def __init__(self, *args, **kwargs):
        super(SegmentAdapter, self).__init__(*args, **kwargs)

    def layer(self, layer_ids=None, request=None):
        """Return mapnik layers and styles."""
        layers = []
        styles = {}

        style = mapnik.Style()
        styles["segmentadapterstyle"] = style

        rule = mapnik.Rule()
        symbol = mapnik.LineSymbolizer(mapnik.Color(255, 100, 100), 4)
        rule.symbols.append(symbol)
        style.rules.append(rule)

        query = """(
            select segment.the_geom
            from lizard_rijnmond_segment segment
        ) as data"""
        default_database = settings.DATABASES['default']
        datasource = mapnik.PostGIS(
            host=default_database['HOST'],
            user=default_database['USER'],
            password=default_database['PASSWORD'],
            dbname=default_database['NAME'],
            table=query,
            )

        layer = mapnik.Layer("Segments", RD)
        layer.datasource = datasource
        layer.styles.append("segmentadapterstyle")
        layers.append(layer)

        return layers, styles


class RiverlineAdapter(WorkspaceItemAdapter):

    def __init__(self, *args, **kwargs):
        super(RiverlineAdapter, self).__init__(*args, **kwargs)
        self.riverline_result_id = self.layer_arguments['riverline_result_id']

    def layer(self, layer_ids=None, request=None):
        """Return mapnik layers and styles."""
        layers = []
        styles = {}
        style = mapnik.Style()
        styles["riverlineadapterstyle"] = style


        for i in range(100):
            rule = mapnik.Rule()
            rule.filter = mapnik.Filter("[value] > %s and [value] < %s" % (
                    i / 10.0, i / 10.0 + 1))
            blueness = 50 + 2 * i
            symbol = mapnik.LineSymbolizer(mapnik.Color(0, 0, blueness), 3)
            rule.symbols.append(symbol)
            style.rules.append(rule)

        # Catch all rule for unknown states:
        rule = mapnik.Rule()
        rule.set_else(True)
        symbol = mapnik.LineSymbolizer(mapnik.Color(100, 100, 100), 3)
        rule.symbols.append(symbol)
        style.rules.append(rule)


        query = """(
            select riverline.the_geom, row.level as value
            from lizard_rijnmond_riverline riverline,
            lizard_rijnmond_riverlineresultdata row
            where riverline.verbose_code = row.location
            and row.riverline_result_id = %s
        ) as data""" % self.riverline_result_id
        logger.info(query)
        default_database = settings.DATABASES['default']
        datasource = mapnik.PostGIS(
            host=default_database['HOST'],
            user=default_database['USER'],
            password=default_database['PASSWORD'],
            dbname=default_database['NAME'],
            table=str(query),
            )

        layer = mapnik.Layer("Riverlines", RD)
        layer.datasource = datasource
        layer.styles.append("riverlineadapterstyle")
        layers.append(layer)

        return layers, styles

