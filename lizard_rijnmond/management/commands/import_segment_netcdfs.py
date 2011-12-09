import copy
import logging
import urllib2
from xml.etree.ElementTree import ElementTree
from pprint import pprint

from optparse import make_option
from datetime import datetime
from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.core.management.base import BaseCommand
from pydap import client

from lizard_rijnmond.models import Measure
from lizard_rijnmond.models import Result

NAMESPACE = 'http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0'
DATASET = '{%s}dataset' % NAMESPACE
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list
    # option_list += make_option(
    #         '--flush',
    #         '-f',
    #         action='store_true',
    #         dest='flush',
    #         default=False,
    #         help='Delete all previously imported data first.'),
    # option_list += make_option(
    #         '--missing-only',
    #         '-m',
    #         action='store_true',
    #         dest='missing_only',
    #         default=False,
    #         help='Import only missing files.'),
    args = ''
    help = ('Import data from the thredds server into the database, ' +
            'replacing imports for which a newer file is on thredds and ' +
            'adding imports from files that were not imported before.')

    def handle(self, *args, **options):
        """Perform the actual import."""
        catalog_root = settings.SEGMENTS_CATALOG_ROOT
        data_root = settings.THREDDS_DATA_ROOT
        # if options.get("flush"):
        if True:
            print "Flushing all previous imports from database..."
            Result.objects.all().delete()
            Measure.objects.all().delete()

        print 'Reading the THREDDS catalog...'
        measure_catalog_url = catalog_root + 'measures/catalog.xml'
        tree = ElementTree()
        tree.parse(urllib2.urlopen(measure_catalog_url))
        datasets = tree.find(DATASET).findall(DATASET)
        measure_urls = [data_root + dataset.get('urlPath')
                        for dataset in datasets]
        print len(measure_urls), "measures found"
        for measure_url in measure_urls:
            netcdf = client.open_url(measure_url)
            code = netcdf.measure.code
            name = netcdf.measure['name']
            measure = Measure(code=code, name=name)
            measure.save()
            print "Added measure", name
