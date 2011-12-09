# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models


class Area(models.Model):
    """Areas from area shapefile (*dijkringen*).

    Columns from the .dbf::

        LENGTH,N,13,11
        CATEGORIE,C,128
        BEHEERDER,C,128
        DIJKRING,C,50
        DKRNR,C,20
        DKRDEEL,C,20
        TRAJECT,C,30
        VAK,C,30
        WV21_WEL,N,19,11

    The ``mapping`` attribute on this class maps the column names to our
    fields. Used by the import_areas management command.

    """
    mapping = {
        'name': 'DIJKRING',
        'maintainer': 'BEHEERDER',
        'code': 'VAK',
        }
    name = models.CharField(max_length=50,
                            null=True,
                            blank=True)
    maintainer = models.CharField(max_length=128,
                                  null=True,
                                  blank=True)
    code = models.CharField(max_length=30,
                            null=True,
                            blank=True)

    the_geom = models.LineStringField(srid=4326)
    objects = models.GeoManager()
