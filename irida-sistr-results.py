import argparse, sys
import csv
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

def get_sample_from_paired(session, paired_path):
	sample_name = None

	input_result=session.get(paired_path)
	if (input_result.ok):
		input_result_json=input_result.json()
		logging.debug(json2str(input_result_json))
		links=input_result_json['resource']['resources'][0]['links']
		sample_href=get_rel_from_links('sample',links)

		sample_json = session.get(sample_href).json()
		logging.debug(json2str(sample_json))

		sample_name = sample_json['resource']['sampleName']
	else:
		input_result.raise_for_status()

	if sample_name is None:
		raise Exception("Could not get sample_name corresponding to " + paired_path)
	else:
		return sample_name

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

				sistr_info={}
				sistr_info['sistr_predictions'] = get_sistr_predictions(session, sistr_analysis_href)
				sistr_info['sample_name'] = get_sample_from_paired(session, paired_path)

				sistr_analysis_list.append(sistr_info)
			else:
				logging.debug('Skipping incompleted sistr submission [id='+sistr['identifier']+']')
		else:
			sistr_submissions_for_user.raise_for_status()
	
	return sistr_analysis_list

def get_sistr_predictions_file(session, sistr_href):
	return session.get(sistr_href, headers={'Accept': 'text/plain'})

def sistr_results_to_table(sistr_results, table_file):
	sistr_writer = csv.writer(table_file, delimiter = "\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

	sistr_writer.writerow([
		'SampleName',
		'Serovar',
		'SerovarAntigen',
		'SerovarCgMLST',
		'QCStatus'
	])

	for result in sistr_results:
		sample_name = result['sample_name']
		sistr_predictions = result['sistr_predictions'][0]
		if (sistr_predictions['serovar_cgmlst'] is None):
			sistr_predictions['serovar_cgmlst']='None'

		sistr_writer.writerow([
			sample_name,
			sistr_predictions['serovar'],
			sistr_predictions['serovar_antigen'],
			sistr_predictions['serovar_cgmlst'],
			sistr_predictions['qc_status']
		])

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Compile SISTR results from an IRIDA instance into a table.')

	parser.add_argument('--irida-url', action='store', dest='irida_url', help='The URL to the IRIDA instance.')
	parser.add_argument('--client-id', action='store', dest='client_id', help='The client id for an IRIDA instance.')
	parser.add_argument('--client-secret', action='store', dest='client_secret', help='The client secret for the IRIDA instance.')
	parser.add_argument('--username', action='store', dest='username', help='The username for the IRIDA instance.')
	parser.add_argument('--password', action='store', dest='password', help='The password for the IRIDA instance.')
	parser.add_argument('--verbose', action='store_true', dest='verbose', help='Turn on verbose logging.')

	if len(sys.argv)==1:
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()
	arg_dict = vars(args)

	if (arg_dict['verbose']):
		logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
	else:
		logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s')
	
	#password=getpass.getpass('Enter password:')
	
	session=get_oauth2_session(arg_dict['client_id'],arg_dict['client_secret'],arg_dict['username'],arg_dict['password'], arg_dict['irida_url'])
	
	sistr_list=get_sistr_submissions(session,'/api/analysisSubmissions/analysisType/sistr')
	
	sistr_results_to_table(sistr_list,sys.stdout)
