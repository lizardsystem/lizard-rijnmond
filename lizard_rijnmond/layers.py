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

    def _ranges(self):
        """Return (from, to, blueness) for legend.

        Range we handle is from 0 to 10 in 1 m steps.

        """
        result = []
        result.append((None, 0, 0))
        for i in range(10):
            from_ = i
            to_ = i + 1
            blueness = 10 + 245/10 * i
            result.append((from_, to_, blueness))
        result.append((to_, None, 255))
        return result

    def legend(self, updates=None):
        result = []
        icon_style_template = {'icon': 'empty.png',
                               'mask': ('empty_mask.png',),
                               'color': (1, 1, 1, 1)}
        for from_, to_, blueness in self._ranges():
            icon_style = icon_style_template.copy()
            icon_style.update({
                    'color': (0, 0, blueness / 255.0, 1)})
            img_url = self.symbol_url(icon_style=icon_style)
            description = ''
            if from_ is not None:
                description += '%s < ' % from_
            description += 'MHW'
            if to_ is not None:
                description += ' < %s' % to_
            legend_row = {'img_url': img_url,
                          'description': description}
            result.append(legend_row)
        return result

    def layer(self, layer_ids=None, request=None):
        """Return mapnik layers and styles."""
        layers = []
        styles = {}
        style = mapnik.Style()
        styles["riverlineadapterstyle"] = style


        for from_, to_, blueness in self._ranges():
            rule = mapnik.Rule()
            if from_ is None:
                rule.filter = mapnik.Filter("[value] < %s" % to_)
            elif to_ is None:
                rule.filter = mapnik.Filter("[value] > %s" % from_)
            else:
                rule.filter = mapnik.Filter("[value] > %s and [value] < %s" % (
                        from_, to_))
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

