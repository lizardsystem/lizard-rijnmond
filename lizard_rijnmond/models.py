# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.contrib.gis.db import models
from django.contrib import admin
from django.utils.translation import ugettext as _

TIME_MAPPING = (
    (50, '2050'),
    (100, '2100'))


class Segment(models.Model):
    """Segments from segment shapefile (dike segments).

    Columns from the ``.dbf``::

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
    fields. Used by the import_segments management command.

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

    class Meta:
        verbose_name = _('Dike segment')
        verbose_name_plural = _('Dike segments')


class Measure(models.Model):
    code = models.CharField(max_length=50,
                            null=True,
                            blank=True)
    name = models.CharField(max_length=128,
                            null=True,
                            blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Measure')
        verbose_name_plural = _('Measures')


class Result(models.Model):
    time = models.IntegerField(
        choices=TIME_MAPPING,
        verbose_name=_('Future date for which the result was calculated'),
        blank=True,
        null=True)
    measure = models.ForeignKey(Measure,
                                blank=True,
                                null=True)

    def __unicode__(self):
        return u'Result for %s at %s' % (self.measure, self.time)

    class Meta:
        verbose_name = _('Result')
        verbose_name_plural = _('Results')


admin.site.register(Result)
admin.site.register(Measure)
admin.site.register(Segment)
