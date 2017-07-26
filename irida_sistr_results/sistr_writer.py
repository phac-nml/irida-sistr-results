import csv
import xlsxwriter
import abc
import logging
from datetime import datetime
from operator import methodcaller

from irida_sistr_results.sistr_info import SampleSistrInfo

class SistrResultsWriter(object):

	def __init__(self,irida_url):
		__metaclass__ = abc.ABCMeta
		self.irida_url=irida_url
		self.row=0
		self.end_of_project=False

	@abc.abstractmethod
	def _write_row(self,row):
		return

	@abc.abstractmethod
	def _write_header(self,header):
		return

	def _formatting(self):
		return

	def _set_end_of_project(self,end_of_project):
		"""Sets whether or not we are at the end row of a project group"""
		self.end_of_project=end_of_project

	def _is_end_of_project(self):
		return self.end_of_project

	def close(self):
		return

	def get_row(self):
		return self.row

	def set_row(self,row):
		self.row=row

	def _get_header_list(self):
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
			'IRIDA Sample Identifer',
			'IRIDA File Pair Identifier',
			'IRIDA Submission Identifier',
			'IRIDA Analysis Date'
		]

	def _format_timestamp(self, timestamp):
		return timestamp.strftime('%Y-%m-%d %H:%M:%S')

	def _get_header_index(self,title):
		"""Gets the particular index from the headers given the title.

		title: The title of the header column.

		returns: The index into the header list.
		"""
		return self._get_header_list().index(title)

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

	def write(self,sistr_results):
		
		self.set_row(0)
		self._write_header(self._get_header_list())
		self.set_row(1)

		for project in sorted(sistr_results.keys(), key=int):
			row_start_project=self.get_row()

			sistr_results_project = sistr_results[project]

			sistr_results_sorted = sorted(sistr_results_project.values(), key=methodcaller('get_sample_created_date'))
			sistr_results_sorted = sorted(sistr_results_sorted, key=methodcaller('get_qc_status_numerical'), reverse=True)
			for index,result in enumerate(sistr_results_sorted):
				# last element in this list
				if (index == len(sistr_results_sorted)-1):
					self._set_end_of_project(True)

				if (not result.has_sistr_results()):
					self._write_row([project,result.get_sample_name(),result.get_qc_status()])
				else:
					self._write_row(self._get_row_list(project,result))
				self.set_row(self.get_row()+1)

			self._set_end_of_project(False)
	
		self._formatting()

class SistrCsvWriter(SistrResultsWriter):

	def __init__(self, irida_url, out_file):
		super(SistrCsvWriter,self).__init__(irida_url)
		self.writer = csv.writer(out_file, delimiter = "\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

	def _write_header(self,header):
		self.writer.writerow(header)

	def _write_row(self,row):
		self.writer.writerow(row)

class SistrCsvWriterShort(SistrCsvWriter):

	def __init__(self, irida_url, out_file):
		super(SistrCsvWriterShort,self).__init__(irida_url,out_file)

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
		
class SistrExcelWriter(SistrResultsWriter):

	def __init__(self, irida_url, out_file):
		super(SistrExcelWriter, self).__init__(irida_url)
		self.workbook = xlsxwriter.Workbook(out_file, {'default_date_format': 'yyyy/mm/dd'})
		self.worksheet = self.workbook.add_worksheet()
		self.index_of_cgmlst_percent = self._get_header_list().index('cgMLST Percent Matching')
		self.index_of_date_formats = [self._get_header_list().index('Sample Created Date'),
						self._get_header_list().index('IRIDA Analysis Date')
						]
		self.percent_format = self.workbook.add_format({'num_format': '0.0%'})

	def _get_header_column_number(self,title):
		"""Gets the particular column number from the headers given the title.

		title: The title of the header column.

		returns: The column number (starting with 1) from the header list.
		"""
		return self._get_header_index(title)+1

	def _get_header_column_letter(self,title):
		"""Gets the particular column letter from the headers given the title.

		title: The title of the header column.

		returns: The column letter (starting with A) from the header list.
		"""
		return self._to_letter(self._get_header_index(title))

	def _range_stitle(self,title):
		"""Gets the particular column letter range from the headers given a single title.

		title: The title of the header column.

		returns: The column range (e.g., A:A) from the header list.
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

