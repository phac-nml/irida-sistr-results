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
		

def sistr_results_to_excel(sistr_results, irida_url, excel_file):
	workbook = xlsxwriter.Workbook(excel_file)
	worksheet = workbook.add_worksheet()

	merged_header_format = workbook.add_format()
	merged_header_format.set_bold()
	merged_header_format.set_align('center')

	header_format = workbook.add_format()
	header_format.set_bold()

	worksheet.merge_range('B1:D1', 'Serovar', merged_header_format)
	worksheet.merge_range('E1:F1', 'QC', merged_header_format)
	worksheet.merge_range('G1:I1', 'IRIDA', merged_header_format)

	row = 1
	col = 0
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

	worksheet.set_column('A:A', 30)
	worksheet.set_column('B:B', 20)
	worksheet.set_column('C:C', 40)
	worksheet.set_column('D:E', 20)
	worksheet.set_column('F:G', 40)
	worksheet.set_column('H:I', 25)

	for item in header:
		worksheet.write(row,col,item, header_format)
		col += 1

	row = 2
	for result in sistr_results.values():
		sample = result['sample']
		paired=result['paired_files'][0]
		sistr_predictions = result['sistr_predictions'][0]

		submission_identifier=result['submission']['identifier']
		submission_url=irida_url
		if irida_url.endswith('/'):
			submission_url += 'analysis/'
		else:
			submission_url += '/analysis/'
		submission_url += submission_identifier

		if (sistr_predictions['serovar_cgmlst'] is None):
			sistr_predictions['serovar_cgmlst']='None'

		row_data = [
			sample['sampleName'],
			sistr_predictions['serovar'],
			sistr_predictions['serovar_antigen'],
			sistr_predictions['serovar_cgmlst'],
			sistr_predictions['qc_status'],
			sistr_predictions['qc_messages'].replace(" | ","\n"),
			submission_url,
			sample['identifier'],
			paired['identifier']
		]

		col = 0
		for item in row_data:
			worksheet.write(row,col,item)
			col += 1

		row += 1

	format_pass = workbook.add_format({'bg_color': '#DFF0D8'})
	format_warning = workbook.add_format({'bg_color': '#FCF8E3'})
	format_fail = workbook.add_format({'bg_color': '#F2DEDE'})
	worksheet.conditional_format('E1:E'+str(row), {'type': 'cell',
						       'criteria': '==',
						       'value': '"PASS"',
						       'format': format_pass})
	worksheet.conditional_format('E1:E'+str(row), {'type': 'cell',
						       'criteria': '==',
						       'value': '"WARNING"',
						       'format': format_warning})
	worksheet.conditional_format('E1:E'+str(row), {'type': 'cell',
						       'criteria': '==',
						       'value': '"FAIL"',
						       'format': format_fail})
						

	workbook.close()

