# -*- coding: utf-8 -*-
# Copyright 2011 Nelen & Schuurmans
import logging
import codecs

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
from lizard_map import coordinates
from lizard_map.models import Workspace
from lizard_map.models import WorkspaceItem
from osgeo import ogr

from lizard_rijnmond.models import Riverline

RIVERLINE_WORKSPACE_ID = 5
RIVERLINE_WORKSPACE_ITEM_ID = 5
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
    for field_name, column_name in Riverline.mapping.items():
        field_indices[field_name] = feature.GetFieldIndex(column_name)
    layer.ResetReading()

    if Riverline.objects.count():
        logger.info("First deleting the existing riverlines...")
        Riverline.objects.all().delete()

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
        riverline = Riverline(**kwargs)
        riverline.save()
        number_of_features += 1
    logger.info("Added %s riverlines", number_of_features)


def setup_special_workspaces():
    Workspace.objects.filter(pk=RIVERLINE_WORKSPACE_ID).delete()
    workspace = Workspace(
        id=RIVERLINE_WORKSPACE_ID,
        name="Riviercenterlijnen")
    workspace.save()
    WorkspaceItem.objects.filter(pk=RIVERLINE_WORKSPACE_ITEM_ID).delete()
    workspace_item = WorkspaceItem(
        id=RIVERLINE_WORKSPACE_ITEM_ID,
        adapter_class='adapter_rijnmond_riverlines',
        workspace=workspace)
    workspace_item.save()
    logger.info("Added special workspace for rijnmond riverlines.")


class Command(BaseCommand):
    args = ""
    help = "Import shapefile with 'dijkringen'. Add shape filename as option."

    def handle(self, *args, **options):
        shapefile_filename = args[0]
        load_shapefile(shapefile_filename)
        setup_special_workspaces()
