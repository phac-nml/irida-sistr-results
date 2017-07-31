import json
import logging
from rauth import OAuth2Service
from urllib.parse import urlsplit, urljoin

logger=logging.getLogger("irida_connector")

class IridaConnector(object):
	"""Low-level connections to the IRIDA REST API"""

	def __init__(self,client_id,client_secret,username,password,base_url,timeout):
		"""Creates a new object for connecting to the IRIDA REST API

		Args:
		    client_id:  The client_id for IRIDA.
		    client_secret:  The client secret for IRIDA.
		    username:  The username of the user for IRIDA.
		    password:  The password for the user.
		    base_url:  The base URL for IRIDA (minis the '/api' part)
		    timeout:  The maximum timeout for any connection to IRIDA.

		Returns: An object which can be used to connect to IRIDA.
		"""
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
		"""A GET request to a particular path in IRIDA.

		Args:
		    path: The path to GET, minus the IRIDA url (e.g., '/projects').

		Returns:  The result of rauth.OAuth2Service.get()
		"""
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
		"""GETs the resources from an IRIDA REST API endpoint (e.g., (get '/projects')['resources']

		Args:
		    path: The path to GET the resources.

		Returns:  The ['resources'] part of the GET JSON response.
		"""
		return self.get(path)['resources']

	def get_file(self, path):
		"""GETs the file contents from an IRIDA REST API endpoint.

		Args:
		    path: The path to GET the file.

		Returns:  The file contents.
		"""
		return self.session.get(path, headers={'Accept': 'text/plain'}, timeout=self._timeout)

	def _log_json(self,json_obj):
		logger.debug(json.dumps(json_obj, sort_keys=True, separators=(',',':'), indent=4))
