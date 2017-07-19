import argparse, sys
import csv, xlsxwriter
import abc
import requests
import json
import logging
import ast
import getpass
from rauth import OAuth2Service

class IridaConnector:

	def __init__(self,client_id,client_secret,username,password,base_url):
		access_token_url=base_url+'/api/oauth/token'
	
		params = {
			"data": {
				"grant_type": "password",
				"client_id": client_id,
				"client_secret": client_secret,
				"username": username,
				"password": password
			}
		}
		
		oauth_service = OAuth2Service(
			client_id=client_id,
			client_secret=client_secret,
			name="irida",
			access_token_url=access_token_url,
			base_url=base_url
		)
		
		token=oauth_service.get_access_token(decoder=ast.literal_eval,**params)
		self.session=oauth_service.get_session(token)

	def get(self,path):
		response=self.session.get(path)
		logging.debug("Getting path="+path)

		if (response.ok):
			self._log_json(response.json())
			return response.json()['resource']
		else:
			response.raise_for_status()

	def get_resources(self,path):
		return self.get(path)['resources']

	def get_file(self, path):
		logging.debug("Getting file from path="+path)
		return self.session.get(path, headers={'Accept': 'text/plain'})

	def _log_json(self,json_obj):
		logging.debug(json.dumps(json_obj, sort_keys=True, separators=(',',':'), indent=4))

class IridaAPI:

	def __init__(self,irida_connector):
		self.irida_connector=irida_connector

	def _get_rel_from_links(self, rel, links):
		href=None
	
		for l in links:
			if (l['rel'] == rel):
				href=l['href']
	
		if (href is None):
			raise Exception("Could not get rel="+rel+" from links="+json2str(links))
		else:
			return href

	def _has_rel_in_links(self, rel, links):
		for l in links:
			if (l['rel'] == rel):
				return True
		return False

	def get_sistr_predictions(self, sistr_analysis_href):
		sistr_pred_json=None
	
		analysis=self.irida_connector.get(sistr_analysis_href)
	
		sistr_href=self._get_rel_from_links('outputFile/sistr-predictions', analysis['links'])
		sistr_pred=self.irida_connector.get_file(sistr_href)
		sistr_pred_json=sistr_pred.json()
	
		if (sistr_pred_json is None):
			raise Exception("Could not get SISTR predictions for sistr " + sistr_analysis_href)
	
		return sistr_pred_json

	def get_sample_from_paired(self, paired_json):
		sample = None
	
		links=paired_json[0]['links']
		sample_href=self._get_rel_from_links('sample',links)
		sample = self.irida_connector.get(sample_href)
	
		if sample is None:
			raise Exception("Could not get sample corresponding to " + paired_path)
		else:
			return sample
	
	
	def get_sistr_results_from_projects(self):
		sistr_list=[]
	
		projects=self.irida_connector.get_resources('/api/projects')
	
		for project in projects:
			sistr_list += self.get_sistr_results_for_project(project['identifier'])
	
		return sistr_list
	
	def get_sistr_results_for_project(self, project):
		sistr_results=[]
	
		sistr_results_for_project=self.irida_connector.get_resources('/api/projects/'+str(project)+'/samples')
	
		for sample in sistr_results_for_project:
			sample_pairs=self.irida_connector.get_resources('/api/samples/'+sample['identifier']+'/pairs')

			for sequencing_object in sample_pairs:
				sistr_info = None

				if (self._has_rel_in_links('analysis/sistr', sequencing_object['links'])):
					sistr_rel=self._get_rel_from_links('analysis/sistr', sequencing_object['links'])

					sistr=self.irida_connector.get(sistr_rel)
					
					sistr_info=self.get_sistr_info_from_submission(sistr)
				else:
					sistr_info = {'sample': sample,
							'paired_files': sequencing_object,
							'has_results': False
							}

				sistr_results.append(sistr_info)
	
		return sistr_results
		
	def get_sistr_info_from_submission(self, submission):
		sistr_info={}
	
		links=submission['links']
		paired_path=self._get_rel_from_links('input/paired',links)
		sistr_analysis_href=self._get_rel_from_links('analysis',links)
		
		unpaired_path=self._get_rel_from_links('input/unpaired',links)
		unpaired_files=self.irida_connector.get_resources(unpaired_path)
		
		if len(unpaired_files) > 0:
			self_href = self._get_rel_from_links('self', submission['links'])
			raise Exception('Error: unpaired files were found for analysis submission ' + self_href + '. SISTR results from unpaired files not currently supported')
		
		paired=self.irida_connector.get_resources(paired_path)
	
		sistr_info['paired_files']=paired
		sistr_info['sistr_predictions'] = self.get_sistr_predictions(sistr_analysis_href)
		sistr_info['has_results'] = True
		sistr_info['sample'] = self.get_sample_from_paired(paired)
		sistr_info['submission'] = submission
	
		return sistr_info
	
	def get_sistr_submissions_for_user(self):
		sistr_submissions_for_user=self.irida_connector.get_resources('/api/analysisSubmissions/analysisType/sistr')
		
		sistr_analysis_list=[]
		for sistr in sistr_submissions_for_user:
			if (sistr['analysisState'] == 'COMPLETED'):
				sistr_analysis_list.append(self.get_sistr_info_from_submission(sistr))
			else:
				logging.debug('Skipping incompleted sistr submission [id='+sistr['identifier']+']')

		return sistr_analysis_list

class IridaSistrResults:

	def __init__(self,irida_api):
		self.irida_api=irida_api

	def get_sistr_results(self,project):
		sistr_results={}
		project_results=self.irida_api.get_sistr_results_for_project(project)

		for result in project_results:
			sample_id=result['sample']['identifier']
			sistr_results[sample_id]=result

		user_results=self.irida_api.get_sistr_submissions_for_user()

		for result in user_results:
			sample_id=result['sample']['identifier']

			if (sample_id in sistr_results and result['has_results']):
				logging.warn("sample_name="+result['sample']['sampleName']+", sample_id="+sample_id+" already has SISTR results, will not update")
			else:
				sistr_results[sample_id]=result

		return sistr_results

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

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Compile SISTR results from an IRIDA instance into a table.')

	parser.add_argument('--irida-url', action='store', dest='irida_url', help='The URL to the IRIDA instance.')
	parser.add_argument('--client-id', action='store', dest='client_id', help='The client id for an IRIDA instance.')
	parser.add_argument('--client-secret', action='store', dest='client_secret', help='The client secret for the IRIDA instance.')
	parser.add_argument('--username', action='store', dest='username', help='The username for the IRIDA instance.')
	parser.add_argument('--password', action='store', dest='password', help='The password for the IRIDA instance. Prompts for password if left blank.')
	parser.add_argument('--verbose', action='store_true', dest='verbose', help='Turn on verbose logging.')
	parser.add_argument('--tabular', action='store_true', dest='tabular', help='Print results to stdout as tab-deliminited file.')
	parser.add_argument('--to-excel-file', action='store', dest='excel_file', help='Print results to the given excel file.')

	if len(sys.argv)==1:
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()
	arg_dict = vars(args)

	if not arg_dict['tabular'] and (arg_dict['excel_file'] is None):
		logging.error("Must use one of --tabular or --to-excel-file [excel-file]")
		parser.print_help()
		sys.exit(1)

	if (arg_dict['verbose']):
		logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
	else:
		logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s')
	
	if arg_dict['password'] is None:
		arg_dict['password']=getpass.getpass('Enter password:')
	
	connector = IridaConnector(arg_dict['client_id'],arg_dict['client_secret'],arg_dict['username'],arg_dict['password'], arg_dict['irida_url'])
	irida_api = IridaAPI(connector)
	irida_results = IridaSistrResults(irida_api)
	
	sistr_list=irida_results.get_sistr_results(1)
	
	if arg_dict['tabular']:
		writer=SistrCsvWriter(arg_dict['irida_url'],sys.stdout)
		writer.write(sistr_list)

	if arg_dict['excel_file'] is not None:
		sistr_results_to_excel(sistr_list,arg_dict['irida_url'], arg_dict['excel_file'])
