import csv
import os
import xlsxwriter
import abc
from datetime import datetime
from operator import methodcaller

from irida_sistr_results.sistr_info import SampleSistrInfo
from irida_sistr_results.version import __version__

class SistrResultsWriter(object):
	"""Abstract class resonsible for writing SISTR results to a table format"""

	def __init__(self,irida_url,appname,username):
		"""Construct a new SistrResultsWriter object corresponding to the passed irida_url

		Args:
		    irida_url: The URL to the IRIDA instance, used to insert URLs into the table
		    appname: The application name.
		    username: The name of the user generating these results.
		"""
		__metaclass__ = abc.ABCMeta
		self.irida_url=irida_url
		self.appname=appname
		self.username=username
		self.row=0
		self.end_of_project=False

	@abc.abstractmethod
	def _write_row(self,row):
		"""Abstract method for writing a particular row for the table"""
		return

	@abc.abstractmethod
	def _write_header(self,header):
		"""Abstract method for writing the table header"""
		return

	def _formatting(self):
		"""Override to implement additional formatting to the table after all rows have finished writing"""
		return

	def _set_end_of_project(self,end_of_project):
		"""Sets whether or not we are at the end row of a project group"""
		self.end_of_project=end_of_project

	def _is_end_of_project(self):
		return self.end_of_project

	def close(self):
		"""Closes writing to a file"""
		return

	def get_row(self):
		"""Gets the current row number"""
		return self.row

	def set_row(self,row):
		"""Sets the current row number

		Args:
			row: The new row number
		"""
		self.row=row

	def _get_header_list(self):
		"""Get a list of header titles for the table

		Return: A list of header titles.
		"""
		return [
			'Project ID',
			'Sample Name',
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
			'IRIDA Analysis Date'
		]

	def _format_timestamp(self, timestamp):
		return timestamp.strftime('%Y-%m-%d %H:%M:%S')

	def _get_header_index(self,title):
		"""Gets the particular index from the headers given the title.

		Args:
		    title: The title of the header column.

		Returns: The index into the header list.
		"""
		return self._get_header_list().index(title)

	def _get_row_list(self,project,result):
		"""Given the project number and result object, creates a list of relavent information to print per row.

		Args:
		    project: The current project identifier.
		    result:  The current SistrInfo result object.

		Return: A list of relevant information for the row
		"""
		return [
			project,
			result.get_sample_name(),
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
			result.get_submission_created_date()
		]

	def _get_no_results_row_list(self,project,result):
		"""Gets a list respresenting no/missing results for a sample.

		Args:
		    project: The current project identifier.
		    result:  The current SistrInfo result object.

		Return: A list of relevant information in the case of a no/missing result row.
		"""

		return [
			project,
			result.get_sample_name(),
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
		]

	def write(self,sistr_results):
		"""Writes out the results to an appropriate file with the appropriate format

		Args:
		    sistr_results:  The SISTR results to write to a table.
		"""
		
		self.set_row(0)
		self._write_header(self._get_header_list())
		self.set_row(1)

		for project in sorted(sistr_results.keys(), key=int):
			row_start_project=self.get_row()

			sistr_results_project = sistr_results[project]

			sistr_results_sorted = sorted(sistr_results_project.values(), key=methodcaller('get_sample_name'))
			sistr_results_sorted = sorted(sistr_results_sorted, key=methodcaller('get_qc_status_numerical'), reverse=True)
			for index,result in enumerate(sistr_results_sorted):
				# last element in this list
				if (index == len(sistr_results_sorted)-1):
					self._set_end_of_project(True)

				if (not result.has_sistr_results()):
					self._write_row(self._get_no_results_row_list(project,result))
				else:
					self._write_row(self._get_row_list(project,result))
				self.set_row(self.get_row()+1)

			self._set_end_of_project(False)
	
		self._formatting()

		self._write_row(["Results generated from "+self.appname+" version="+__version__ + " connecting to IRIDA=" + self.irida_url + " as user=" + self.username + " on date=" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

class SistrCsvWriter(SistrResultsWriter):
	"""An abstact writer used to create CSV/tab-delimited files"""

	def __init__(self, irida_url, appname, username, out_file):
		super(SistrCsvWriter,self).__init__(irida_url, appname, username)
		out_file_h = open(out_file, 'w')
		self.writer = csv.writer(out_file_h, delimiter = "\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

	def _write_header(self,header):
		self.writer.writerow(header)

	def _write_row(self,row):
		self.writer.writerow(row)

	def _get_row_list(self,project,result):
		return [
			project,
			result.get_sample_name(),
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
			"{0:.1f}".format(result.get_cgmlst_matching_proportion()*100)+'%',
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
			result.get_submission_created_date()
		]

class SistrCsvWriterShort(SistrCsvWriter):
	"""Creates a shortened version of the results in a tab-delimited format"""

	def __init__(self, irida_url, appname, username, out_file):
		super(SistrCsvWriterShort,self).__init__(irida_url,appname,username,out_file)

	def _get_header_list(self):
		return [
			'Project ID',
			'Sample Name',
			'QC Status',
			'Created Date',
			'Serovar (overall)',
			'Serovar (antigen)',
			'Serovar (cgMLST)',
			'cgMLST Alleles Matching',
			'cgMLST Percent Matching',
			'IRIDA Analysis URL'
		]

	def _get_row_list(self,project,result):
		return [
			project,
			result.get_sample_name(),
			result.get_qc_status(),
			result.get_sample_created_date(),
			result.get_serovar(),
			result.get_serovar_antigen(),
			result.get_serovar_cgmlst(),
			result.get_cgmlst_matching_alleles(),
			"{0:.1f}".format(result.get_cgmlst_matching_proportion()*100)+'%',
			result.get_submission_url(self.irida_url)
		]

	def _get_no_results_row_list(self,project,result):
		return [
			project,
			result.get_sample_name(),
			result.get_qc_status(),
			None,
			None,
			None,
			None,
			None,
			None,
			None
		]
		
class SistrExcelWriter(SistrResultsWriter):
	"""A writer object for writing SISTR results to an excel spreadsheet"""

	def __init__(self, irida_url, appname, username, out_file):
		super(SistrExcelWriter, self).__init__(irida_url, appname, username)
		self.workbook = xlsxwriter.Workbook(out_file, {'default_date_format': 'yyyy/mm/dd'})
		self.worksheet = self.workbook.add_worksheet()
		self.index_of_cgmlst_percent = self._get_header_list().index('cgMLST Percent Matching')
		self.index_of_date_formats = [self._get_header_list().index('Sample Created Date'),
						self._get_header_list().index('IRIDA Analysis Date')
						]
		self.percent_format = self.workbook.add_format({'num_format': '0.0%'})

	def _get_header_column_number(self,title):
		"""Gets the particular column number from the headers given the title.

		Args:
		    title: The title of the header column.

		Returns: The column number (starting with 1) from the header list.
		"""
		return self._get_header_index(title)+1

	def _get_header_column_letter(self,title):
		"""Gets the particular column letter from the headers given the title.

		Args:
		    title: The title of the header column.

		Returns: The column letter (starting with A) from the header list.
		"""
		return self._to_letter(self._get_header_index(title))

	def _range_stitle(self,title):
		"""Gets the particular column letter range from the headers given a single title.

		Args:
		    title: The title of the header column.

		Returns: The column range (e.g., A:A) from the header list.
		"""
		return self._range_title(title,title)

	def _range_title(self,start_title,end_title):
		scol=self._get_header_index(start_title)
		ecol=self._get_header_index(end_title)
		return self._to_range_col_1(scol,ecol)

	def _to_letter(self,col):
		return chr(ord('A')+col)

	def _to_range_col(self,start_col,end_col):
		return self._to_letter(start_col)+':'+self._to_letter(end_col)

	def _to_range_col_1(self,start_col,end_col):
		return self._to_letter(start_col)+'1:'+self._to_letter(end_col)+'1'

	def _to_range_row(self,start_title,start_row,end_row):
		start_col=self._get_header_column_letter(start_title)
		return start_col+str(start_row)+':'+start_col+str(end_row)

	def _to_range(self,start_row,end_row,start_col,end_col):
		return self._to_letter(start_col)+str(start_row)+':'+self._to_letter(end_col)+str(end_row)

	def _write_header(self, header):
		merged_header_format = self.workbook.add_format()
		merged_header_format.set_bold()
		merged_header_format.set_align('center')

		header_format = self.workbook.add_format()
		header_format.set_bold()

		col = 0
		for item in header:
			self.worksheet.write(self.get_row(),col,item, header_format)
			col += 1

		self.worksheet.set_column(self._range_stitle('Project ID'), 15)
		self.worksheet.set_column(self._range_title('Sample Name', 'Serogroup'), 20)
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
				self.worksheet.write(self.get_row(),col,item,self._get_percent_format())
			elif col in self.index_of_date_formats:
				self.worksheet.write(self.get_row(),col,item,self._get_date_format())
			else:
				self.worksheet.write(self.get_row(),col,item,self._get_regular_format())
			col += 1

		if self._is_end_of_project():
			bottom_format=self.workbook.add_format({'bottom': 5})
			self.worksheet.set_row(self.get_row(),None,bottom_format)

	def _get_percent_format(self):
		if (self._is_end_of_project()):
			return self.workbook.add_format({'num_format': '0.0%', 'bottom': 5})
		else:
			return self.workbook.add_format({'num_format': '0.0%'})

	def _get_date_format(self):
		if (self._is_end_of_project()):
			return self.workbook.add_format({'num_format': 'yyyy/mm/dd', 'bottom': 5})
		else:
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
		form_range=self._to_range_row('QC Status',1,self.get_row())
		self.worksheet.conditional_format(form_range, {'type': 'cell',
									 'criteria': '==',
									 'value': '"PASS"',
									 'format': format_pass})
		self.worksheet.conditional_format(form_range, {'type': 'cell',
									 'criteria': '==',
									 'value': '"WARNING"',
									 'format': format_warning})
		self.worksheet.conditional_format(form_range, {'type': 'cell',
									 'criteria': '==',
									 'value': '"FAIL"',
									 'format': format_fail})
		self.worksheet.conditional_format(form_range, {'type': 'cell',
									 'criteria': '==',
									 'value': '"MISSING"',
									 'format': format_missing})
		self.worksheet.freeze_panes(1,3)

	def close(self):
		self.workbook.close()

