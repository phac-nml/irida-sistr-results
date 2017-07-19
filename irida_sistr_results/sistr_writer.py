import csv
import xlsxwriter
import abc
import logging

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

	def write(self,sistr_results):
		
		header = [
			'Sample Name',
			'Serovar',
			'Serovar Antigen',
			'Serovar cgMLST',
			'QC Status',
			'QC Messages',
			'URL',
			'IRIDA Sample Identifer',
			'IRIDA File Pair Identifier'
		]

		self._write_header(header)
		
		for result in sistr_results.values():
			if (not result.has_sistr_results()):
				self._write_row([result.get_sample_name()])
			else:
				self._write_row([
					result.get_sample_name(),
					result.get_serovar(),
					result.get_serovar_antigen(),
					result.get_serovar_cgmlst(),
					result.get_qc_status(),
					result.get_qc_messages(),
					result.get_submission_url(self.irida_url),
					result.get_sample_id(),
					result.get_paired_id()
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

	def _write_header(self, header):

		merged_header_format = self.workbook.add_format()
		merged_header_format.set_bold()
		merged_header_format.set_align('center')

		header_format = self.workbook.add_format()
		header_format.set_bold()

		self.worksheet.merge_range('B1:D1', 'Serovar', merged_header_format)
		self.worksheet.merge_range('E1:F1', 'QC', merged_header_format)
		self.worksheet.merge_range('G1:I1', 'IRIDA', merged_header_format)

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
		logging.warning("Formatting row="+str(self.row))
		format_pass = self.workbook.add_format({'bg_color': '#DFF0D8'})
		format_warning = self.workbook.add_format({'bg_color': '#FCF8E3'})
		format_fail = self.workbook.add_format({'bg_color': '#F2DEDE'})
		self.worksheet.conditional_format('E1:E'+str(self.row), {'type': 'cell',
									 'criteria': '==',
									 'value': '"PASS"',
									 'format': format_pass})
		self.worksheet.conditional_format('E1:E'+str(self.row), {'type': 'cell',
									 'criteria': '==',
									 'value': '"WARNING"',
									 'format': format_warning})
		self.worksheet.conditional_format('E1:E'+str(self.row), {'type': 'cell',
									 'criteria': '==',
									 'value': '"FAIL"',
									 'format': format_fail})

	def close(self):
		self.workbook.close()

