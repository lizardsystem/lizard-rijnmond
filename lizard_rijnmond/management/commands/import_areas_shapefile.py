# -*- coding: utf-8 -*-
# Copyright 2011 Nelen & Schuurmans
import logging
import codecs

from osgeo import ogr
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
from lizard_map import coordinates
# from lizard_map.models import Workspace
# from lizard_map.models import WorkspaceItem

from lizard_rijnmond.models import Area
# from deltaportaal.views import RIVERMAP_WORKSPACE_ID
# from deltaportaal.views import RIVERMAP_WORKSPACE_ITEM_ID

SOURCE_ENCODING = "windows-1252"

logger = logging.getLogger(__name__)


def load_shapefile(shapefile_filename):
    original_srs = ogr.osr.SpatialReference()
    original_srs.ImportFromProj4(coordinates.RD)
    target_srs = ogr.osr.SpatialReference()
    target_srs.ImportFromEPSG(4326)

    # coordinate_transformation =
    # ogr.osr.CoordinateTransformation(original_srs, target_srs)
    drv = ogr.GetDriverByName('ESRI Shapefile')
    source = drv.Open(shapefile_filename)
    layer = source.GetLayer()
    feature = layer.next()
    field_indices = {}
    for field_name, column_name in Area.mapping.items():
        field_indices[field_name] = feature.GetFieldIndex(column_name)
    layer.ResetReading()

    if Area.objects.count():
        logger.info("First deleting the existing areas...")
        Area.objects.all().delete()

    number_of_features = 0
    for feature in layer:
        geom = feature.GetGeometryRef()
        #geom.Transform(coordinate_transformation)
        geom.FlattenTo2D()
        kwargs = {}
        geometry = GEOSGeometry(geom.ExportToWkt())
        kwargs['the_geom'] = geometry
        for field_name, index in field_indices.items():

            kwargs[field_name] = codecs.decode(feature.GetField(index),
                                               SOURCE_ENCODING)
        area = Area(**kwargs)
        area.save()
        number_of_features += 1
    logger.info("Added %s areas", number_of_features)


# def setup_special_workspaces():
#     Workspace.objects.filter(pk=RIVERMAP_WORKSPACE_ID).delete()
#     workspace = Workspace(
#         id=RIVERMAP_WORKSPACE_ID,
#         name="Riviersegmenten")
#     workspace.save()
#     WorkspaceItem.objects.filter(pk=RIVERMAP_WORKSPACE_ITEM_ID).delete()
#     WorkspaceItem.objects.filter(pk=RIVERMAP_WORKSPACE_ITEM_ID + 1).delete()
#     workspace_item = WorkspaceItem(
#         id=RIVERMAP_WORKSPACE_ITEM_ID,
#         adapter_class='adapter_riverpoint',
#         workspace=workspace)
#     workspace_item.save()
#     workspace_item2 = WorkspaceItem(
#         id=RIVERMAP_WORKSPACE_ITEM_ID + 1,
#         adapter_class='selected_measures',
#         workspace=workspace)
#     workspace_item2.save()
#     logger.info("Added special workspace for river segments.")


class Command(BaseCommand):
    args = ""
    help = "Import shapefile with 'dijkringen'. Add shape filename as option."

    def handle(self, *args, **options):
        shapefile_filename = args[0]
        load_shapefile(shapefile_filename)
        # setup_special_workspaces()
