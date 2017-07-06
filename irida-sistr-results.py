import requests
import json
import logging
import ast
import getpass
from rauth import OAuth2Service

#logging.basicConfig(level=logging.DEBUG)

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

def get_sistr_submissions(session, path):
	sistr_submissions_for_user=session.get('/api/analysisSubmissions/analysisType/sistr')
	
	sistr_analysis_list=[]
	if (sistr_submissions_for_user.ok):
		sistr_list=sistr_submissions_for_user.json()['resource']['resources']
		for sistr in sistr_list:
			if (sistr['analysisState'] == 'COMPLETED'):
				logging.debug(json2str(sistr))

				paired_path=get_rel_from_links('input/paired',sistr['links'])

				sistr_info={}
				sistr_info['href'] = get_rel_from_links('analysis',sistr['links'])
				sistr_info['sample_name'] = get_sample_from_paired(session, paired_path)

				sistr_analysis_list.append(sistr_info)
			else:
				logging.debug('Skipping incompleted sistr submission [id='+sistr['identifier']+']')
		else:
			sistr_submissions_for_user.raise_for_status()
	
	return sistr_analysis_list

def get_sistr_predictions(session, sistr_href):
	return session.get(sistr_href, headers={'Accept': 'text/plain'})

client_id='jupiter'
client_secret='0Th4YM9hHl1Nlu932X8FK3SQ0wYKqJlHJW3x679Q2S'
username = 'admin'
password='Password1'
base_url='http://localhost:8080'

#password=getpass.getpass('Enter password:')

session=get_oauth2_session(client_id,client_secret,username,password,base_url)

sistr_list=get_sistr_submissions(session,'/api/analysisSubmissions/analysisType/sistr')

#sistr_submissions_for_user=session.get('/api/analysisSubmissions/analysisType/sistr')

sistr_results=[]
for sistr_info in sistr_list:
	a=sistr_info['href']
	sistr_result={}
	sistr_result['sample_name']=sistr_info['sample_name']

	analysis=session.get(a)
	if (analysis.ok):
		analysis_json=analysis.json()
		logging.debug(json2str(analysis_json))

		sistr_href=get_rel_from_links('outputFile/sistr-predictions', analysis_json['resource']['links'])
		sistr_pred=get_sistr_predictions(session, sistr_href)
		sistr_pred_json=sistr_pred.json()
		logging.debug(json2str(sistr_pred_json))

		sistr_result['sistr_predictions']=sistr_pred_json

	sistr_results.append(sistr_result)

print "Sample_name\tSerovar\tSerovar_antigen\tSerovar_cgmlst\tqc_status"
for s in sistr_results:
	sample_name=s['sample_name']
	sistr_predictions=s['sistr_predictions'][0]
	if (sistr_predictions['serovar_cgmlst'] is None):
		sistr_predictions['serovar_cgmlst']='None'
	print sample_name+"\t"+sistr_predictions['serovar']+"\t"+sistr_predictions['serovar_antigen']+"\t"+sistr_predictions['serovar_cgmlst']+"\t"+sistr_predictions['qc_status']
