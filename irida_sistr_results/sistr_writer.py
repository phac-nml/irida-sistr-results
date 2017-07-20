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

	def _format_timestamp(self, timestamp):
		return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

	def write(self,sistr_results):
		
		header = [
			'Sample Name',
			'Created Date',
			'Serovar (overall)',
			'Serovar (antigen)',
			'Serovar (cgMLST)',
			'Serogroup',
			'H1',
			'H2',
			'O-antigen',
			'QC Status',
			'QC Messages',
			'URL',
			'IRIDA Sample Identifer',
			'IRIDA File Pair Identifier',
			'IRIDA Submission Identifier',
			'IRIDA Analysis Date'
		]

		self._write_header(header)
		
		for result in sistr_results.values():
			if (not result.has_sistr_results()):
				self._write_row([result.get_sample_name()])
			else:
				self._write_row([
					result.get_sample_name(),
					self._format_timestamp(result.get_sample_created_date()),
					result.get_serovar(),
					result.get_serovar_antigen(),
					result.get_serovar_cgmlst(),
					result.get_serogroup(),
					result.get_h1(),
					result.get_h2(),
					result.get_o_antigen(),
					result.get_qc_status(),
					result.get_qc_messages(),
					result.get_submission_url(self.irida_url),
					result.get_sample_id(),
					result.get_paired_id(),
					result.get_submission_identifier(),
					self._format_timestamp(result.get_submission_created_date())
				])

		self._formatting()

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

	def _to_letter(self,col):
		return chr(ord('A')+col)

	def _to_range_col(self,start_col,end_col):
		return self._to_letter(start_col)+'1:'+self._to_letter(end_col)+'1'

	def _to_range_row(self,start_col,start_row,end_row):
		return self._to_letter(start_col)+str(start_row)+':'+self._to_letter(start_col)+str(end_row)

	def _set_formatting_ranges(self,header):
		for i,v in enumerate(header):
			if v == 'Serovar (overall)':
				self.serovar_sc = i
			elif v == 'O-antigen':
				self.serovar_ec = i
			elif v == 'QC Status':
				self.qc_sc = i
				self.qc_fc = i
			elif v == 'QC Messages':
				self.qc_ec = i
			elif v == 'URL':
				self.irida_sc = i
			elif v == 'IRIDA Analysis Date':
				self.irida_ec = i
			

	def _write_header(self, header):

		self._set_formatting_ranges(header)

		merged_header_format = self.workbook.add_format()
		merged_header_format.set_bold()
		merged_header_format.set_align('center')

		header_format = self.workbook.add_format()
		header_format.set_bold()

		self.worksheet.merge_range(self._to_range_col(self.serovar_sc,self.serovar_ec), 'Serovar', merged_header_format)
		self.worksheet.merge_range(self._to_range_col(self.qc_sc,self.qc_ec), 'QC', merged_header_format)
		self.worksheet.merge_range(self._to_range_col(self.irida_sc,self.irida_ec), 'IRIDA', merged_header_format)

		col = 0
		for item in header:
			self.worksheet.write(self.row,col,item, header_format)
			col += 1

		self.worksheet.set_column('A:A', 30)
		self.worksheet.set_column('B:B', 20)
		self.worksheet.set_column('C:C', 40)
		self.worksheet.set_column('D:E', 20)
		self.worksheet.set_column('F:G', 40)
		self.worksheet.set_column('H:I', 25)

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
		form_range=self._to_range_row(self.qc_fc,1,self.row)
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

	def close(self):
		self.workbook.close()

