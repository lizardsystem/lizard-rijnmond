# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from lizard_map import coordinates
from lizard_map.workspace import WorkspaceItemAdapter
import mapnik

from lizard_rijnmond.models import Riverline
from lizard_rijnmond.models import RiverlineResult
from lizard_rijnmond.models import RiverlineResultData

MAX_SEARCH_RESULTS = 3

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

        layer = mapnik.Layer("Segments", coordinates.RD)
        layer.datasource = datasource
        layer.styles.append("segmentadapterstyle")
        layers.append(layer)

        return layers, styles


class RiverlineAdapter(WorkspaceItemAdapter):

    def __init__(self, *args, **kwargs):
        super(RiverlineAdapter, self).__init__(*args, **kwargs)
        self.riverline_result_id = self.layer_arguments['riverline_result_id']
        self.riverline_result = RiverlineResult.objects.get(
            pk=self.riverline_result_id)

    def _reference_ranges(self):
        """Return (from, to, blueness) for legend.

        Range we handle is from 0 to 10 in 1 m steps.

        """
        result = []
        for i in range(20):
            from_ = 0.5 * i
            to_ = from_ + 0.5
            blueness = int(10 + 245/20 * i)
            color = (0, 0, blueness)
            result.append((from_, to_, color))
        result.append((to_, None, color))
        return result

    def _ranges(self):
        result = []
        for i in range(10):
            from_ = -100 + 10 * i
            to_ = from_ + 10
            redness = 0 + 18 * i
            color = (255, redness, redness)
            result.append((from_, to_, color))
        for i in range(10):
            from_ = 10 * i
            to_ = from_ + 10
            greenness = 180 - 18 * i
            color = (greenness, 255, greenness)
            result.append((from_, to_, color))
        print result
        return result

    def legend(self, updates=None):
        result = []
        icon_style_template = {'icon': 'empty.png',
                               'mask': ('empty_mask.png',),
                               'color': (1, 1, 1, 1)}
        if self.riverline_result.is_reference:
            range_method = self._reference_ranges
        else:
            range_method = self._ranges
        for from_, to_, color in range_method():
            icon_style = icon_style_template.copy()
            color = (color[0] /255.0,
                     color[1] /255.0,
                     color[2] /255.0)
            icon_style.update({
                    'color': color})
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

        if self.riverline_result.is_reference:
            range_method = self._reference_ranges
            level_field = 'level'
        else:
            range_method = self._ranges
            level_field = 'relative_level'
        for from_, to_, color in range_method():
            rule = mapnik.Rule()
            if from_ is None:
                rule.filter = mapnik.Filter("[value] < %s" % to_)
            elif to_ is None:
                rule.filter = mapnik.Filter("[value] > %s" % from_)
            else:
                rule.filter = mapnik.Filter("[value] > %s and [value] < %s" % (
                        from_, to_))
            symbol = mapnik.LineSymbolizer(
                mapnik.Color(color[0], color[1], color[2]), 3)
            rule.symbols.append(symbol)
            style.rules.append(rule)

        # Catch all rule for unknown states:
        rule = mapnik.Rule()
        rule.set_else(True)
        symbol = mapnik.LineSymbolizer(mapnik.Color(100, 100, 100), 3)
        rule.symbols.append(symbol)
        style.rules.append(rule)

        query = """(
            select riverline.the_geom, row.%s as value
            from lizard_rijnmond_riverline riverline,
            lizard_rijnmond_riverlineresultdata row
            where riverline.verbose_code = row.location
            and row.riverline_result_id = %s
        ) as data""" % (level_field, self.riverline_result_id)
        logger.info(query)
        default_database = settings.DATABASES['default']
        datasource = mapnik.PostGIS(
            host=default_database['HOST'],
            user=default_database['USER'],
            password=default_database['PASSWORD'],
            dbname=default_database['NAME'],
            table=str(query),
            )

        layer = mapnik.Layer("Riverlines", coordinates.RD)
        layer.datasource = datasource
        layer.styles.append("riverlineadapterstyle")
        layers.append(layer)

        return layers, styles

    def search(self, google_x, google_y, radius=None):
        """Return closest cell.

        What we return is in lizard-map's quite elaborate dict format,
        but the main goal is that we return the identifier: a dict
        with the cell id and the hydro model layer id.  The
        ``.graph()`` and ``.html()`` methods use that identifier data.

        """
        # x, y = coordinates.google_to_rd(google_x, google_y)
        radius = radius * 15
        logger.debug("Searching for cell near %s, %s with radius %s",
                     google_x, google_y, radius)
        # pt = Point(coordinates.rd_to_wgs84(x, y), 4326)
        # pt = Point((google_x, google_y), coordinates.GOOGLE)
        #pt = Point(coordinates.google_to_wgs84(google_x, google_y), 4326)
        pt = Point(coordinates.google_to_rd(google_x, google_y), coordinates.RD)
        logger.debug(pt)
        rls = []
        for rl in Riverline.objects.all().centroid():
            distance = (rl.centroid.x - pt.x) ** 2 + (rl.centroid.y - pt.y) ** 2
            distance = distance ** 0.5
            rl.distance = distance
            rls.append(rl)
        rls.sort(cmp=lambda x, y: cmp(x.distance, y.distance))
        matching_riverlines = rls[:3]

        # matching_riverlines = Riverline.objects.filter(
        #     the_geom__distance_lte=(pt, D(m=radius))).distance(pt).order_by(
        #     'distance')
        logger.debug("Found %s matching riverlines.",
                     len(matching_riverlines))
        for rl in matching_riverlines:
            logger.debug("%s", rl.verbose_code)
        logger.debug("Searching for result data for riverline result %s",
                     self.riverline_result_id)
        riverline_result_datas = RiverlineResultData.objects.filter(
            riverline_result=int(self.riverline_result_id)).filter(
            riverline__in=matching_riverlines)
        logger.debug("%s matching riverlinedata results",
                     riverline_result_datas.count())
        result = []
        for matching_riverline in matching_riverlines:
            for riverline_result_data in riverline_result_datas:
                if not riverline_result_data.riverline == matching_riverline:
                    continue
                result.append({'distance': matching_riverline.distance,
                               'name': 'not used',
                               'workspace_item': self.workspace_item,
                               'identifier': {'riverline_result_data_id':
                                                  riverline_result_data.id},
                               'google_coords': (google_x, google_y),
                               'object': riverline_result_data})
        return result

    def html(self, snippet_group=None, identifiers=None, layout_options=None):
        """
        """
        return super(RiverlineAdapter, self).html_default(
            snippet_group=snippet_group,
            identifiers=identifiers,
            layout_options=layout_options,
            template="lizard_rijnmond/riverline_result_data_popup.html",
            extra_render_kwargs=identifiers[0]
        )

    def location(self, riverline_result_data_id=None, layout=None):
        logger.debug("Returning riverline result data for %s",
                     riverline_result_data_id)
        return RiverlineResultData.objects.get(pk=riverline_result_data_id)
