import argparse, sys
import csv, xlsxwriter
import requests
import json
import logging
import ast
import getpass
from rauth import OAuth2Service

def json2str(json_obj):
	return json.dumps(json_obj, sort_keys=True, separators=(',',':'), indent=4)

def get_oauth2_session(client_id,client_secret,username,password,base_url):
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
	session=oauth_service.get_session(token)

	return session

def get_rel_from_links(rel, links):
	href=None

	for l in links:
		if (l['rel'] == rel):
			href=l['href']

	if (href is None):
		raise Exception("Could not get rel="+rel+" from links="+json2str(links))
	else:
		return href

def get_sample_from_paired(session, paired_json):
	sample = None

	links=paired_json[0]['links']
	sample_href=get_rel_from_links('sample',links)
	sample_json = session.get(sample_href).json()
	logging.debug(json2str(sample_json))

	sample = sample_json['resource']

	if sample is None:
		raise Exception("Could not get sample corresponding to " + paired_path)
	else:
		return sample

def get_sistr_predictions(session, sistr_analysis_href):
	sistr_pred_json=None

	analysis=session.get(sistr_analysis_href)
	if (analysis.ok):
		analysis_json=analysis.json()
		logging.debug(json2str(analysis_json))

		sistr_href=get_rel_from_links('outputFile/sistr-predictions', analysis_json['resource']['links'])
		sistr_pred=get_sistr_predictions_file(session, sistr_href)
		sistr_pred_json=sistr_pred.json()
		logging.debug(json2str(sistr_pred_json))
	else:
		analysis.raise_for_status()

	if (sistr_pred_json is None):
		raise Exception("Could not get SISTR predictions for sistr " + sistr_analysis_href)

	return sistr_pred_json

def get_sistr_submissions(session, path):
	sistr_submissions_for_user=session.get('/api/analysisSubmissions/analysisType/sistr')
	
	sistr_analysis_list=[]
	if (sistr_submissions_for_user.ok):
		sistr_list=sistr_submissions_for_user.json()['resource']['resources']
		for sistr in sistr_list:
			if (sistr['analysisState'] == 'COMPLETED'):
				logging.debug(json2str(sistr))

				paired_path=get_rel_from_links('input/paired',sistr['links'])
				sistr_analysis_href=get_rel_from_links('analysis',sistr['links'])

				unpaired_path=get_rel_from_links('input/unpaired',sistr['links'])
				unpaired_files=session.get(unpaired_path)

				if len(unpaired_files.json()['resource']['resources']) > 0:
					self_href = get_rel_from_links('self', sistr['links'])
					raise Exception('Error: unpaired files were found for analysis submission ' + self_href + '. SISTR results from unpaired files not currently supported')

				sistr_info={}
				paired=session.get(paired_path)

				if (paired.ok):
					logging.debug(json2str(paired.json()))

					paired_json=paired.json()['resource']['resources']

					sistr_info['paired_files']=paired_json
					sistr_info['sistr_predictions'] = get_sistr_predictions(session, sistr_analysis_href)
					sistr_info['sample'] = get_sample_from_paired(session, paired_json)
					sistr_info['submission'] = sistr

					sistr_analysis_list.append(sistr_info)
				else:
					paired.raise_for_status()
			else:
				logging.debug('Skipping incompleted sistr submission [id='+sistr['identifier']+']')
		else:
			sistr_submissions_for_user.raise_for_status()
	
	return sistr_analysis_list

def get_sistr_predictions_file(session, sistr_href):
	return session.get(sistr_href, headers={'Accept': 'text/plain'})

def sistr_results_to_excel(sistr_results, irida_url, excel_file):
	workbook = xlsxwriter.Workbook(excel_file)
	worksheet = workbook.add_worksheet()
	header_format = workbook.add_format()

	header_format.set_bold()

	row = 0
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

	row = 1
	for result in sistr_results:
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
			sistr_predictions['qc_messages'].replace('|',"\n"),
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

def sistr_results_to_table(sistr_results, table_file, irida_url):
	sistr_writer = csv.writer(table_file, delimiter = "\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

	sistr_writer.writerow([
		'SampleName',
		'Serovar',
		'SerovarAntigen',
		'SerovarCgMLST',
		'QCStatus',
		'URL'
	])

	for result in sistr_results:
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

		sistr_writer.writerow([
			sample['sampleName'],
			sistr_predictions['serovar'],
			sistr_predictions['serovar_antigen'],
			sistr_predictions['serovar_cgmlst'],
			sistr_predictions['qc_status'],
			submission_url
		])

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
	
	session=get_oauth2_session(arg_dict['client_id'],arg_dict['client_secret'],arg_dict['username'],arg_dict['password'], arg_dict['irida_url'])
	
	sistr_list=get_sistr_submissions(session,'/api/analysisSubmissions/analysisType/sistr')
	
	if arg_dict['tabular']:
		sistr_results_to_table(sistr_list,sys.stdout, arg_dict['irida_url'])

	if arg_dict['excel_file'] is not None:
		sistr_results_to_excel(sistr_list,arg_dict['irida_url'], arg_dict['excel_file'])
