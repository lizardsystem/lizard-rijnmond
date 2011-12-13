# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging

from django.contrib.gis.db import models
from django.contrib import admin
from django.utils.translation import ugettext as _

TIME_MAPPING = (
    (50, '2050'),
    (100, '2100'))
logger = logging.getLogger(__name__)


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


class Riverline(models.Model):
    """Riverlines from riverline shapefile (river centerlines).

    Columns from the ``.dbf``::

        ITEM1,C,50
        ITEM2,C,50

    The ``mapping`` attribute on this class maps the column names to our
    fields. Used by the import_rd_river_shapefile management command.

    """
    mapping = {
        'code': 'ITEM1',
        'name': 'ITEM2',
        }
    code = models.CharField(max_length=30,
                            null=True,
                            blank=True)
    name = models.CharField(max_length=50,
                            null=True,
                            blank=True)
    verbose_code = models.CharField(max_length=128,
                                    null=True,
                                    blank=True)

    the_geom = models.LineStringField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.verbose_code

    class Meta:
        verbose_name = _('Dike riverline')
        verbose_name_plural = _('Dike riverlines')

    def save(self, *args, **kwargs):
        km = self.code.split('_')[1]
        km = int(float(km))
        self.verbose_code = '%s km %4d' % (self.name, km)
        super(Riverline, self).save(*args, **kwargs)


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


class Scenario(models.Model):
    name = models.CharField(max_length=20,
                            null=True,
                            blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Scenario')
        verbose_name_plural = _('Scenarios')


class Strategy(models.Model):
    name = models.CharField(max_length=128,
                            null=True,
                            blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Strategy')
        verbose_name_plural = _('Strategies')


class Year(models.Model):
    name = models.CharField(max_length=20,
                            null=True,
                            blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Year')
        verbose_name_plural = _('Years')


class RiverlineResult(models.Model):
    strategy = models.ForeignKey(Strategy,
                                blank=True,
                                null=True)
    scenario = models.ForeignKey(Scenario,
                                 blank=True,
                                 null=True)
    year = models.ForeignKey(Year,
                             blank=True,
                             null=True)

    def __unicode__(self):
        return _('Result for %(strategy)s and %(scenario)s at %(year)s') % {
            'strategy': self.strategy,
            'scenario': self.scenario,
            'year': self.year}

    class Meta:
        verbose_name = _('Result')
        verbose_name_plural = _('Results')


class RiverlineResultData(models.Model):
    riverline_result = models.ForeignKey(RiverlineResult,
                                         blank=True,
                                         null=True)
    level = models.FloatField(blank=True, null=True)
    location = models.CharField(max_length=128,
                                null=True,
                                blank=True)
    riverline = models.ForeignKey(Riverline,
                                  blank=True,
                                  null=True)

    def save(self, *args, **kwargs):
        riverlines = Riverline.objects.filter(verbose_code=self.location)
        if len(riverlines) > 1:
            logger.debug("Riverline for %s found multiple times.", self.location)
        if len(riverlines) == 0:
            logger.warn("Riverline for %s not found.", self.location)
        else:
            riverline = riverlines[0]
            self.riverline = riverline
        super(RiverlineResultData, self).save(*args, **kwargs)


admin.site.register(Result)
admin.site.register(Measure)
admin.site.register(Segment)
admin.site.register(Riverline)
admin.site.register(RiverlineResult)
admin.site.register(RiverlineResultData)
admin.site.register(Scenario)
admin.site.register(Strategy)
admin.site.register(Year)
