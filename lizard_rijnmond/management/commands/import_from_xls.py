import logging
import os

from django.core.management.base import BaseCommand
import xlrd

from lizard_rijnmond.models import Scenario
from lizard_rijnmond.models import Strategy
from lizard_rijnmond.models import Year
from lizard_rijnmond.models import RiverlineResult
from lizard_rijnmond.models import RiverlineResultData

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import data from a collection of xls files."

    def rows_from_xls(self, filename, header_row_starts_with):
        """Return list of dicts from xls file."""
        logger.debug("Reading xls file %s", filename)
        xls = xlrd.open_workbook(filename)
        assert xls.nsheets == 1
        sheet = xls.sheet_by_index(0)
        logger.debug("%s rows and %s columns", sheet.nrows, sheet.ncols)
        header_row_index = None
        for row_index in range(sheet.nrows):
            if sheet.cell_value(row_index, 0) == header_row_starts_with:
                logger.debug("First row that starts with '%s' has index %s",
                             header_row_starts_with, row_index)
                header_row_index = row_index
        if header_row_index is None:
            logger.error("Row that starts with '%s' not found in %s",
                         header_row_starts_with, filename)
            return
        headers = [sheet.cell_value(header_row_index, i)
                   for i in range(sheet.ncols)]
        headers = [header.strip().replace(' ', '_').lower()
                   for header in headers]
        logger.debug("Found headers: %s", headers)
        rows = []
        for row_index in range(header_row_index + 1, sheet.nrows):
            row = {}
            if not sheet.cell_value(row_index, 0):
                # Empty row.
                continue
            for column_index, key in enumerate(headers):
                row[key] = sheet.cell_value(row_index, column_index)
            rows.append(row)
        return rows

    def handle(self, *args, **options):
        if not args:
            logger.error("Give me a .xls filename")
            return
        base_file = os.path.abspath(args[0])
        base_dir = os.path.dirname(base_file)
        overview = self.rows_from_xls(base_file, 'Code')

        # Flush.
        Scenario.objects.all().delete()
        Strategy.objects.all().delete()
        Year.objects.all().delete()
        RiverlineResult.objects.all().delete()

        scenarios = set([row['klimaatscenario'] for row in overview])
        for scenario_name in scenarios:
            scenario = Scenario(name=scenario_name)
            scenario.save()
        logger.info("Scenarios found: %s", scenarios)
        strategies = set([row['strategie'] for row in overview])
        for strategy_name in strategies:
            strategy = Strategy(name=strategy_name)
            strategy.save()
        logger.info("Strategies found: %s", strategies)
        years = set([row['zichtjaar'] for row in overview])
        for year_name in years:
            year = Year(name=year_name)
            year.save()
        logger.info("Years found: %s", years)
        for row in overview:
            filename = os.path.join(base_dir, row['code'] + '.xls')
            if not os.path.exists(filename):
                logger.warn("%s does not exist", filename)
                row['available'] = False
                continue
            logger.debug("%s exists", filename)
            row['available'] = True

            if 'MHW' in filename:
                result = self.rows_from_xls(filename, 'ID')
                if result is None:
                    continue
                field_names = result[0].keys()
                level_field = [field for field in field_names
                               if field.startswith('waterstand')][0]
                logger.debug("Water level field is %s", level_field)
                riverline_result = RiverlineResult(
                    strategy=Strategy.objects.get(name=row['strategie']),
                    scenario=Scenario.objects.get(name=row['klimaatscenario']),
                    year=Year.objects.get(name=row['zichtjaar']))
                riverline_result.save()
                count = 0
                for line in result:
                    riverline_result_data = RiverlineResultData(
                        riverline_result=riverline_result,
                        level=line[level_field],
                        location=line['locatie'])
                    riverline_result_data.save()
                    count += 1
                logger.info("Saved %s results for %s", count, riverline_result)
