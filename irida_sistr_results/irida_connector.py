import json
import logging
import ast
from rauth import OAuth2Service

class IridaConnector(object):

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
