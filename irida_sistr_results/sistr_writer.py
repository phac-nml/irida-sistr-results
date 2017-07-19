import csv
import xlsxwriter
import abc
import logging

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

	@abc.abstractmethod
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
			sample = result['sample']
	
			if (not result['has_results']):
				self._write_row([sample['sampleName']])
			else:
				paired=result['paired_files'][0]
				sistr_predictions = result['sistr_predictions'][0]
		
				submission_identifier=result['submission']['identifier']
				submission_url=self.irida_url
				if submission_url.endswith('/'):
					submission_url += 'analysis/'
				else:
					submission_url += '/analysis/'
				submission_url += submission_identifier
		
				if (sistr_predictions['serovar_cgmlst'] is None):
					sistr_predictions['serovar_cgmlst']='None'
		
				self._write_row([
					sample['sampleName'],
					sistr_predictions['serovar'],
					sistr_predictions['serovar_antigen'],
					sistr_predictions['serovar_cgmlst'],
					sistr_predictions['qc_status'],
					sistr_predictions['qc_messages'],
					submission_url,
					sample['identifier'],
					paired['identifier']
				])

class SistrCsvWriter(SistrResultsWriter):

	def __init__(self, irida_url, out_file):
		super(SistrCsvWriter,self).__init__(irida_url)
		self.writer = csv.writer(out_file, delimiter = "\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

	def _write_header(self,header):
		self.writer.writerow(header)

	def _write_row(self,row):
		self.writer.writerow(row)

	def close(self):
		return
		
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

	def close(self):
		self.workbook.close()

