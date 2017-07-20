import csv
import xlsxwriter
import abc
import logging
from datetime import datetime

from sistr_info import SampleSistrInfo

class SistrResultsWriter(object):

	def __init__(self,irida_url):
		__metaclass__ = abc.ABCMeta
		self.irida_url=irida_url

	@abc.abstractmethod
	def _write_row(self,row):
		return

	@abc.abstractmethod
	def _write_header(self,header):
		return

	def _formatting(self):
		return

	def close(self):
		return

	def _get_header_list(self):
		return [
			'Sample Name',
			'QC Status',
			'QC Messages',
			'Created Date',
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
			'URL',
			'IRIDA Sample Identifer',
			'IRIDA File Pair Identifier',
			'IRIDA Submission Identifier',
			'IRIDA Analysis Date'
		]

	def _format_timestamp(self, timestamp):
		return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

	def _get_header_index(self,title):
		"""Gets the particular index from the headers given the title.

		title: The title of the header column.

		returns: The index into the header list.
		"""
		return self._get_header_list().index(title)

	def _get_row_list(self,result):
		return [
			result.get_sample_name(),
			result.get_qc_status(),
			result.get_qc_messages(),
			self._format_timestamp(result.get_sample_created_date()),
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
			str(result.get_cgmlst_matching_proportion()*100)+'%',
			result.get_cgmlst_sequence_type(),
			result.get_mash_subspecies(),
			result.get_mash_serovar(),
			result.get_mash_genome(),
			result.get_mash_distance(),
			result.get_submission_url(self.irida_url),
			result.get_sample_id(),
			result.get_paired_id(),
			result.get_submission_identifier(),
			self._format_timestamp(result.get_submission_created_date())
		]

	def write(self,sistr_results):
		
		self._write_header(self._get_header_list())
		
		for result in sistr_results.values():
			if (not result.has_sistr_results()):
				self._write_row([result.get_sample_name(),'MISSING'])
			else:
				self._write_row(self._get_row_list(result))

		self._formatting()

class SistrCsvWriterShort(SistrResultsWriter):

	def __init__(self, irida_url, out_file):
		super(SistrCsvWriterShort,self).__init__(irida_url)
		self.writer = csv.writer(out_file, delimiter = "\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

	def _write_header(self,header):
		self.writer.writerow(header)

	def _write_row(self,row):
		self.writer.writerow(row)

	def _get_header_list(self):
		return [
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

	def _get_row_list(self,result):
		return [
			result.get_sample_name(),
			result.get_qc_status(),
			self._format_timestamp(result.get_sample_created_date()),
			result.get_serovar(),
			result.get_serovar_antigen(),
			result.get_serovar_cgmlst(),
			result.get_cgmlst_matching_alleles(),
			"{0:.1f}".format(result.get_cgmlst_matching_proportion()*100)+'%',
			result.get_submission_url(self.irida_url)
		]

class SistrCsvWriter(SistrResultsWriter):

	def __init__(self, irida_url, out_file):
		super(SistrCsvWriter,self).__init__(irida_url)
		self.writer = csv.writer(out_file, delimiter = "\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

	def _write_header(self,header):
		self.writer.writerow(header)

	def _write_row(self,row):
		self.writer.writerow(row)
		
class SistrExcelWriter(SistrResultsWriter):

	def __init__(self, irida_url, out_file):
		super(SistrExcelWriter, self).__init__(irida_url)
		self.workbook = xlsxwriter.Workbook(out_file)
		self.worksheet = self.workbook.add_worksheet()
		self.row=1

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

	def _write_header(self, header):
		merged_header_format = self.workbook.add_format()
		merged_header_format.set_bold()
		merged_header_format.set_align('center')

		header_format = self.workbook.add_format()
		header_format.set_bold()
		self.worksheet.merge_range(self._range_title('QC Status', 'QC Messages'), 'QC', merged_header_format)
		self.worksheet.merge_range(self._range_title('Serovar (overall)', 'O-antigen'), 'Serovar', merged_header_format)
		self.worksheet.merge_range(self._range_title('cgMLST Subspecies', 'cgMLST Sequence Type'), 'cgMLST', merged_header_format)
		self.worksheet.merge_range(self._range_title('Mash Subspecies', 'Mash Distance'), 'Mash', merged_header_format)
		self.worksheet.merge_range(self._range_title('URL', 'IRIDA Analysis Date'), 'IRIDA', merged_header_format)

		col = 0
		for item in header:
			self.worksheet.write(self.row,col,item, header_format)
			col += 1

		self.worksheet.set_column(self._range_title('Sample Name', 'Serogroup'), 20)
		self.worksheet.set_column(self._range_stitle('H1'), 10)
		self.worksheet.set_column(self._range_stitle('H2'), 10)
		self.worksheet.set_column(self._range_title('O-antigen', 'cgMLST Subspecies'), 20)
		self.worksheet.set_column(self._range_title('cgMLST Matching Genome', 'cgMLST Sequence Type'), 25)
		self.worksheet.set_column(self._range_title('Mash Subspecies', 'Mash Serovar'), 20)
		self.worksheet.set_column(self._range_title('Mash Matching Genome Name', 'IRIDA Analysis Date'), 30)

		self.row += 1

	def _write_row(self, row):
		col = 0
		for item in row:
			self.worksheet.write(self.row,col,item)
			col += 1

		self.row += 1

	def _formatting(self):
		format_pass = self.workbook.add_format({'bg_color': '#DFF0D8'})
		format_warning = self.workbook.add_format({'bg_color': '#FCF8E3'})
		format_fail = self.workbook.add_format({'bg_color': '#F2DEDE'})
		format_missing = self.workbook.add_format({'bg_color': '#BBBBBB'})
		form_range=self._to_range_row('QC Status',1,self.row)
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
		self.worksheet.freeze_panes(2,2)

	def close(self):
		self.workbook.close()

