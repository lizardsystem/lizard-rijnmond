# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging

from django.conf import settings
from lizard_map.coordinates import RD
from lizard_map.workspace import WorkspaceItemAdapter
import mapnik

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
