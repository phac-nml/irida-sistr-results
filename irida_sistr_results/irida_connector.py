import json
import logging
from rauth import OAuth2Service
from urllib.parse import urlsplit, urljoin

logger=logging.getLogger("irida_connector")

class IridaConnector(object):

	def __init__(self,client_id,client_secret,username,password,base_url,timeout):
		base_url=base_url.rstrip('/')
		self._base_path=urlsplit(base_url).path
		self._timeout=timeout

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
		
		token=oauth_service.get_access_token(decoder=json.loads,**params)
		self.session=oauth_service.get_session(token)

	def get(self,path):
		path=self._join_path(path)
		logger.debug("Getting path="+path)
		response=self.session.get(path,timeout=self._timeout)

		if (response.ok):
			self._log_json(response.json())
			return response.json()['resource']
		else:
			response.raise_for_status()

	def _join_path(self,path):
		if (self._base_path is None or self._base_path == ''):
			return path
		# If passed full URL like http://localhost/path, don't add on base_path
		elif (urlsplit(path).scheme != ''):
			return path
		else:
			if (path[0] == '/'):
				return self._base_path + path
			else:
				return self._base_path + '/' + path

	def get_resources(self,path):
		return self.get(path)['resources']

	def get_file(self, path):
		return self.session.get(path, headers={'Accept': 'text/plain'}, timeout=self._timeout)

	def _log_json(self,json_obj):
		logger.debug(json.dumps(json_obj, sort_keys=True, separators=(',',':'), indent=4))
