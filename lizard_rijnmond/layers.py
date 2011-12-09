# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging

from django.conf import settings
from lizard_map.coordinates import RD
from lizard_map.workspace import WorkspaceItemAdapter
import mapnik

logger = logging.getLogger(__name__)


class AreaAdapter(WorkspaceItemAdapter):

    def __init__(self, *args, **kwargs):
        super(AreaAdapter, self).__init__(*args, **kwargs)

    def layer(self, layer_ids=None, request=None):
        """Return mapnik layers and styles."""
        layers = []
        styles = {}

        style = mapnik.Style()
        styles["areaadapterstyle"] = style

        rule = mapnik.Rule()
        symbol = mapnik.LineSymbolizer(mapnik.Color(255, 100, 100), 4)
        rule.symbols.append(symbol)
        style.rules.append(rule)

        query = """(
            select area.the_geom
            from lizard_rijnmond_area area
        ) as data"""
        default_database = settings.DATABASES['default']
        datasource = mapnik.PostGIS(
            host=default_database['HOST'],
            user=default_database['USER'],
            password=default_database['PASSWORD'],
            dbname=default_database['NAME'],
            table=query,
            )

        layer = mapnik.Layer("Areas", RD)
        layer.datasource = datasource
        layer.styles.append("areaadapterstyle")
        layers.append(layer)

        return layers, styles
