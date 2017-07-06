import requests
import json
import ast
import getpass
from rauth import OAuth2Service

def decoder(d):
	return ast.literal_eval(d)

client_id='jupiter'
client_secret='0Th4YM9hHl1Nlu932X8FK3SQ0wYKqJlHJW3x679Q2S'
username = 'admin'
password='Password1'
base_url='http://localhost:8080'
access_token_url=base_url+'/api/oauth/token'

#password=getpass.getpass('Enter password:')

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

token=oauth_service.get_access_token(decoder=decoder,**params)
session=oauth_service.get_session(token)

sistr_sub=session.get('/api/analysisSubmissions/analysisType/sistr')
#sistr_sub=session.get('/irida/api/analysisSubmissions')

analysis_list=[]
if (sistr_sub.ok):
	sistr_sub_json=sistr_sub.json()
#	print json.dumps(sistr_sub_json, sort_keys=True, separators=(',',':'), indent=4)
	sistr_list=sistr_sub_json['resource']['resources']
#	print json.dumps(sistr_list,sort_keys=True, separators=(',',':'), indent=4)
	for s in sistr_list:
		if (s['analysisState'] == 'COMPLETED' and (s['workflowId'] == 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7' or s['workflowId'] == 'e559af58-a560-4bbd-997e-808bfbe026e2')):
			analysis_info={}
			for l in s['links']:
				if l['rel'] == 'analysis':
					analysis_info['href'] = l['href']
				if l['rel'] == 'input/paired':
					analysis_info['input'] = l['href']
			analysis_list.append(analysis_info)

sistr_results=[]
for ainfo in analysis_list:
	a=ainfo['href']
	ainput=ainfo['input']
	sistr_result={}

	input_obj=session.get(ainput)
	if (input_obj.ok):
		input_obj_json=input_obj.json()
		links=input_obj_json['resource']['resources'][0]['links']
		for l in links:
			if l['rel'] == 'sample':
				sample_json = session.get(l['href']).json()
				sample_name = sample_json['resource']['sampleName']
				sistr_result['sample_name'] = sample_name

	analysis=session.get(a)
	if (analysis.ok):
		analysis_json=analysis.json()
#		print json.dumps(analysis_json, sort_keys=True, separators=(',',':'), indent=4)

		for l in analysis_json['resource']['links']:
			if l['rel'] == 'outputFile/sistr-predictions':
				sistr_pred=session.get(l['href'], headers={'Accept': 'text/plain'})
				#print json.dumps(sistr_pred.json(), sort_keys=True, separators=(',',':'), indent=4)
				sistr_result['sistr_predictions']=sistr_pred.json()
	sistr_results.append(sistr_result)

print "Sample_name\tSerovar\tSerovar_antigen\tSerovar_cgmlst\tqc_status"
for s in sistr_results:
	sample_name=s['sample_name']
	sistr_predictions=s['sistr_predictions'][0]
	if (sistr_predictions['serovar_cgmlst'] is None):
		sistr_predictions['serovar_cgmlst']='None'
	print sample_name+"\t"+sistr_predictions['serovar']+"\t"+sistr_predictions['serovar_antigen']+"\t"+sistr_predictions['serovar_cgmlst']+"\t"+sistr_predictions['qc_status']
