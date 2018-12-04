import abc
import csv
from collections import OrderedDict
from datetime import datetime
from operator import methodcaller

import xlsxwriter

from irida_sistr_results.version import __version__


class SistrResultsWriter(object):
    """Abstract class resonsible for writing SISTR results to a table format"""

    def __init__(self, irida_url, appname, command_line, username, include_reportable_status=True, sample_created_min_date=None):
        """
        Construct a new SistrResultsWriter object corresponding to the passed irida_url

        :param irida_url: The URL to the IRIDA instance, used to insert URLs into the table
        :param appname: The application name.
        :param command_line: The command line string used by the application.
        :param username: The name of the user generating these results.
        :param include_reportable_status: Whether or not to include the reportable status to output.
        :param sample_created_min_date: The minimum date for including samples.
        """
        __metaclass__ = abc.ABCMeta
        self.irida_url = irida_url
        self.appname = appname
        self.command_line = command_line
        self.username = username
        self.row = 0
        self.end_of_project = False
        self.include_reportable_status = include_reportable_status
        self.sample_created_min_date = sample_created_min_date

    @abc.abstractmethod
    def _write_row(self, row):
        """Abstract method for writing a particular row for the table"""
        return

    @abc.abstractmethod
    def _write_header(self, header):
        """Abstract method for writing the table header"""
        return

    def _formatting(self):
        """Override to implement additional formatting to the table after all rows have finished writing"""
        return

    def _set_end_of_project(self, end_of_project):
        """Sets whether or not we are at the end row of a project group"""
        self.end_of_project = end_of_project

    def _is_end_of_project(self):
        return self.end_of_project

    def _finish(self):
        return

    def close(self):
        """Closes writing to a file"""
        return

    def get_row(self):
        """Gets the current row number"""
        return self.row

    def set_row(self, row):
        """
        Sets the current row number

        :param row: The new row number
        """
        self.row = row

    def _get_header_list(self):
        """
        Get a list of header titles for the table

        :return: A list of header titles.
        """
        header_list = [
            'Project ID',
            'Sample Name'
        ]

        if self.include_reportable_status:
            header_list.append('Reportable Serovar Status')

        header_list.extend([
            'QC Status',
            'Serovar (overall)',
            'Serovar (antigen)',
            'Serovar (cgMLST)',
            'Serogroup',
            'H1',
            'H2',
            'O-antigen',
            'cgMLST Subspecies',
            'cgMLST Matching Genome',
            'Alleles Matching Genome',
            'cgMLST Percent Matching',
            'cgMLST Sequence Type',
            'Mash Subspecies',
            'Mash Serovar',
            'Mash Matching Genome Name',
            'Mash Distance',
            'QC Messages',
            'IRIDA URL',
            'Sample Created Date',
            'IRIDA Sample Identifier',
            'IRIDA File Pair Identifier',
            'IRIDA Submission Identifier',
            'IRIDA Analysis Date',
            'IRIDA Workflow Version',
            'IRIDA Workflow ID',
        ])

        return header_list

    def _format_timestamp(self, timestamp):
        return timestamp.isoformat(sep=' ')

    def _get_header_index(self, title):
        """
        Gets the particular index from the headers given the title.

        :param title: The title of the header column.

        :return: The index into the header list.
        """
        return self._get_header_list().index(title)

    def _get_row_list(self, project, result):
        """
        Given the project number and result object, creates a list of relavent information to print per row.

        :param project: The current project identifier.
        :param result:  The current SistrInfo result object.

        :return: A list of relevant information for the row
        """
        row_list = [
            project,
            result.get_sample_name()
        ]

        if self.include_reportable_status:
            row_list.append(result.get_reportable_serovar_status())

        row_list.extend([
            result.get_qc_status(),
            result.get_serovar(),
            result.get_serovar_antigen(),
            result.get_serovar_cgmlst(),
            result.get_serogroup(),
            result.get_h1(),
            result.get_h2(),
            result.get_o_antigen(),
            result.get_cgmlst_subspecies(),
            result.get_cgmlst_genome(),
            result.get_cgmlst_matching_alleles(),
            result.get_cgmlst_matching_proportion(),
            result.get_cgmlst_sequence_type(),
            result.get_mash_subspecies(),
            result.get_mash_serovar(),
            result.get_mash_genome(),
            result.get_mash_distance(),
            result.get_qc_messages(),
            result.get_submission_url(self.irida_url),
            result.get_sample_created_date(),
            result.get_sample_id(),
            result.get_paired_id(),
            result.get_submission_identifier(),
            result.get_submission_created_date(),
            result.get_submission_workflow_version(),
            result.get_submission_workflow_id(),
        ])

        return row_list

    def _get_no_results_row_list(self, project, result):
        """
        Gets a list respresenting no/missing results for a sample.

        :param project: The current project identifier.
        :param result:  The current SistrInfo result object.

        :return: A list of relevant information in the case of a no/missing result row.
        """
        row_list = [
            project,
            result.get_sample_name(),
        ]

        if self.include_reportable_status:
            row_list.append(result.get_reportable_serovar_status())

        row_list.extend([
            result.get_qc_status(),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            result.get_sample_created_date(),
            result.get_sample_id(),
            None,
            None,
            None,
            None,
            None,
        ])

        return row_list

    def _get_irida_sistr_run_info(self):
        """
        Gets information about the run of this irida-sistr-results script.
        :return: Information in the form of a Dict of key/value pairs.
        """
        info = OrderedDict()
        info['appname'] = self.appname
        info['version'] = __version__
        info['command_line'] = self.command_line
        info['irida_url'] = self.irida_url
        info['username'] = self.username
        info['app_run_date'] = datetime.now()

        if self.sample_created_min_date:
            info['sample_created_min_date'] = self.sample_created_min_date

        return info

    def write(self, sistr_results):
        """
        Writes out the results to an appropriate file with the appropriate format

        :param sistr_results:  The SISTR results to write to a table.
        :return: None
        """
        self.set_row(0)
        self._write_header(self._get_header_list())
        self.set_row(1)

        for project in sorted(sistr_results.keys(), key=int):
            row_start_project = self.get_row()

            sistr_results_project = sistr_results[project]

            sistr_results_sorted = sorted(sistr_results_project.values(), key=methodcaller('get_sample_name'))
            sistr_results_sorted = sorted(sistr_results_sorted, key=methodcaller('get_qc_status_numerical'),
                                          reverse=True)

            if self.include_reportable_status:
                sistr_results_sorted = sorted(sistr_results_sorted, key=methodcaller('get_reportable_status_numerical'),
                                              reverse=True)

            for index, result in enumerate(sistr_results_sorted):
                # last element in this list
                if (index == len(sistr_results_sorted) - 1):
                    self._set_end_of_project(True)

                if (not result.has_sistr_results()):
                    self._write_row(self._get_no_results_row_list(project, result))
                else:
                    self._write_row(self._get_row_list(project, result))
                self.set_row(self.get_row() + 1)

            self._set_end_of_project(False)

        self._formatting()
        self._finish()


class SistrCsvWriter(SistrResultsWriter):
    """An abstact writer used to create CSV/tab-delimited files"""

    def __init__(self, irida_url, appname, command_line, username, out_file, include_reportable_status=True,
                 sample_created_min_date=None):
        super(SistrCsvWriter, self).__init__(irida_url, appname, command_line, username, include_reportable_status,
                                             sample_created_min_date)
        out_file_h = open(out_file, 'w')
        self.writer = csv.writer(out_file_h, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

    def _write_header(self, header):
        run_info = self._get_irida_sistr_run_info()
        sample_create_msg = ' using only samples created after ' + self.sample_created_min_date.isoformat(
            sep=' ') if 'sample_created_min_date' in run_info else ''
        self._write_row([
            "# Results generated from {} version={} connecting to IRIDA={} as user={} on date={} {}".format(
                run_info['appname'],
                run_info['version'],
                run_info['irida_url'],
                run_info['username'],
                run_info['app_run_date'],
                sample_create_msg)])
        self._write_row(["# Using command [{}]".format(run_info['command_line'])])
        self.writer.writerow(header)

    def _write_row(self, row):
        self.writer.writerow(row)

    def _get_row_list(self, project, result):
        row_list = [
            project,
            result.get_sample_name()
        ]

        if self.include_reportable_status:
            row_list.append(result.get_reportable_serovar_status())

        row_list.extend([
            result.get_qc_status(),
            result.get_serovar(),
            result.get_serovar_antigen(),
            result.get_serovar_cgmlst(),
            result.get_serogroup(),
            result.get_h1(),
            result.get_h2(),
            result.get_o_antigen(),
            result.get_cgmlst_subspecies(),
            result.get_cgmlst_genome(),
            result.get_cgmlst_matching_alleles(),
            "{0:.1f}".format(result.get_cgmlst_matching_proportion() * 100) + '%',
            result.get_cgmlst_sequence_type(),
            result.get_mash_subspecies(),
            result.get_mash_serovar(),
            result.get_mash_genome(),
            result.get_mash_distance(),
            result.get_qc_messages(),
            result.get_submission_url(self.irida_url),
            result.get_sample_created_date(),
            result.get_sample_id(),
            result.get_paired_id(),
            result.get_submission_identifier(),
            result.get_submission_created_date(),
            result.get_submission_workflow_version(),
            result.get_submission_workflow_id(),
        ])

        return row_list


class SistrExcelWriter(SistrResultsWriter):
    """A writer object for writing SISTR results to an excel spreadsheet"""

    def __init__(self, irida_url, appname, command_line, username, out_file, include_reportable_status=True,
                 sample_created_min_date=None):
        super(SistrExcelWriter, self).__init__(irida_url, appname, command_line, username, include_reportable_status,
                                               sample_created_min_date)
        self.workbook = xlsxwriter.Workbook(out_file, {'default_date_format': 'yyyy/mm/dd'})
        self.worksheet = self.workbook.add_worksheet('Data')
        self.index_of_cgmlst_percent = self._get_header_list().index('cgMLST Percent Matching')
        self.index_of_date_formats = [self._get_header_list().index('Sample Created Date'),
                                      self._get_header_list().index('IRIDA Analysis Date')
                                      ]
        self.percent_format = self.workbook.add_format({'num_format': '0.0%'})

    def _get_header_column_number(self, title):
        """
        Gets the particular column number from the headers given the title.

        :param title: The title of the header column.

        :return: The column number (starting with 1) from the header list.
        """
        return self._get_header_index(title) + 1

    def _get_header_column_letter(self, title):
        """
        Gets the particular column letter from the headers given the title.

        :param title: The title of the header column.

        :return: The column letter (starting with A) from the header list.
        """
        return self._to_letter(self._get_header_index(title))

    def _range_stitle(self, title):
        """
        Gets the particular column letter range from the headers given a single title.

        :param title: The title of the header column.

        :return: The column range (e.g., A:A) from the header list.
        """
        return self._range_title(title, title)

    def _range_title(self, start_title, end_title):
        scol = self._get_header_index(start_title)
        ecol = self._get_header_index(end_title)
        return self._to_range_col_1(scol, ecol)

    def _to_letter(self, col):
        MAX_ALPHABET = 26

        if col < MAX_ALPHABET:
            return chr(ord('A') + col)
        else:
            return self._to_letter(int(col / MAX_ALPHABET)) + self._to_letter(int(col % MAX_ALPHABET))

    def _to_range_col(self, start_col, end_col):
        return self._to_letter(start_col) + ':' + self._to_letter(end_col)

    def _to_range_col_1(self, start_col, end_col):
        return self._to_letter(start_col) + '1:' + self._to_letter(end_col) + '1'

    def _to_range_row(self, start_title, start_row, end_row):
        start_col = self._get_header_column_letter(start_title)
        return start_col + str(start_row) + ':' + start_col + str(end_row)

    def _to_range(self, start_row, end_row, start_col, end_col):
        return self._to_letter(start_col) + str(start_row) + ':' + self._to_letter(end_col) + str(end_row)

    def _write_header(self, header):
        merged_header_format = self.workbook.add_format()
        merged_header_format.set_bold()
        merged_header_format.set_align('center')

        header_format = self.workbook.add_format()
        header_format.set_bold()

        col = 0
        for item in header:
            self.worksheet.write(self.get_row(), col, item, header_format)
            col += 1

        self.worksheet.set_column(self._range_stitle('Project ID'), 15)
        self.worksheet.set_column(self._range_title('Sample Name', 'Serogroup'), 25)
        self.worksheet.set_column(self._range_stitle('H1'), 10)
        self.worksheet.set_column(self._range_stitle('H2'), 10)
        self.worksheet.set_column(self._range_title('O-antigen', 'cgMLST Subspecies'), 20)
        self.worksheet.set_column(self._range_title('cgMLST Matching Genome', 'cgMLST Sequence Type'), 25)
        self.worksheet.set_column(self._range_title('Mash Subspecies', 'Mash Serovar'), 20)
        self.worksheet.set_column(self._range_title('Mash Matching Genome Name', 'IRIDA Analysis Date'), 30)

    def _write_row(self, row):
        col = 0
        for item in row:
            if col == self.index_of_cgmlst_percent:
                self.worksheet.write(self.get_row(), col, item, self._get_percent_format())
            elif col in self.index_of_date_formats:
                self.worksheet.write(self.get_row(), col, item, self._get_date_format())
            else:
                self.worksheet.write(self.get_row(), col, item, self._get_regular_format())
            col += 1

        if self._is_end_of_project():
            bottom_format = self.workbook.add_format({'bottom': 5})
            self.worksheet.set_row(self.get_row(), None, bottom_format)

    def _get_percent_format(self):
        if (self._is_end_of_project()):
            return self.workbook.add_format({'num_format': '0.0%', 'bottom': 5})
        else:
            return self.workbook.add_format({'num_format': '0.0%'})

    def _get_date_format(self):
        if (self._is_end_of_project()):
            return self.workbook.add_format({'num_format': 'yyyy/mm/dd', 'bottom': 5})
        else:
            return self._get_default_date_format()

    def _get_default_date_format(self):
        return self.workbook.add_format({'num_format': 'yyyy/mm/dd'})

    def _get_regular_format(self):
        if (self._is_end_of_project()):
            return self.workbook.add_format({'bottom': 5})
        else:
            return self.workbook.add_format()

    def _formatting(self):
        format_pass = self.workbook.add_format({'bg_color': '#DFF0D8'})
        format_warning = self.workbook.add_format({'bg_color': '#FCF8E3'})
        format_fail = self.workbook.add_format({'bg_color': '#F2DEDE'})
        format_missing = self.workbook.add_format({'bg_color': '#BBBBBB'})
        format_range_qc_status = self._to_range_row('QC Status', 1, self.get_row())

        self.worksheet.conditional_format(format_range_qc_status, {'type': 'cell',
                                                                   'criteria': '==',
                                                                   'value': '"PASS"',
                                                                   'format': format_pass})
        self.worksheet.conditional_format(format_range_qc_status, {'type': 'cell',
                                                                   'criteria': '==',
                                                                   'value': '"WARNING"',
                                                                   'format': format_warning})
        self.worksheet.conditional_format(format_range_qc_status, {'type': 'cell',
                                                                   'criteria': '==',
                                                                   'value': '"FAIL"',
                                                                   'format': format_fail})
        self.worksheet.conditional_format(format_range_qc_status, {'type': 'cell',
                                                                   'criteria': '==',
                                                                   'value': '"MISSING"',
                                                                   'format': format_missing})

        if self.include_reportable_status:
            format_range_reportable = self._to_range_row('Reportable Serovar Status', 1, self.get_row())
            self.worksheet.conditional_format(format_range_reportable, {'type': 'cell',
                                                                        'criteria': '==',
                                                                        'value': '"PASS"',
                                                                        'format': format_pass})
            self.worksheet.conditional_format(format_range_reportable, {'type': 'cell',
                                                                        'criteria': '==',
                                                                        'value': '"FAIL"',
                                                                        'format': format_fail})
        self.worksheet.freeze_panes(1, 3)

    def _finish(self):
        info_worksheet = self.workbook.add_worksheet('Settings')
        info = self._get_irida_sistr_run_info()

        date_format = self._get_default_date_format()

        row = 0
        for k, v in info.items():
            info_worksheet.write(row, 0, k)

            if k == 'app_run_date' or k == 'sample_created_min_date':
                info_worksheet.write(row, 1, v, date_format)
            else:
                info_worksheet.write(row, 1, v)
            info_worksheet.write(row, 1, v)
            row += 1

        bold_format = self.workbook.add_format()
        bold_format.set_bold()

        info_worksheet.set_column('A:A', 25, bold_format)
        info_worksheet.set_column('B:B', 20)

    def close(self):
        """Closes the workbook"""
        self.workbook.close()
