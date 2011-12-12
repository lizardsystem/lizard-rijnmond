import logging
import os

from django.core.management.base import BaseCommand
import xlrd

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
            logger.error("Row that starts with '%s' not found",
                         header_row_starts_with)
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
        scenarios = set([row['klimaatscenario'] for row in overview])
        logger.info("Scenarios found: %s", scenarios)
        strategies = set([row['strategie'] for row in overview])
        logger.info("Strategies found: %s", strategies)
        years = set([row['zichtjaar'] for row in overview])
        logger.info("Years found: %s", years)
        for row in overview:
            filename = os.path.join(base_dir, row['code'] + '.xls')
            if not os.path.exists(filename):
                logger.warn("%s does not exist", filename)
                continue
            logger.debug("%s exists", filename)
