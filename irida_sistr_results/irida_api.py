import logging
import json
from requests.exceptions import HTTPError

from irida_sistr_results.sistr_info import SampleSistrInfo
from irida_sistr_results.SistrResultsException import SistrResultsException

LOGLEVEL_TRACE=5

logger=logging.getLogger("irida-api")

class IridaAPI(object):
	"""A class for dealing with higher-level API functionality of the IRIDA REST API."""

	def __init__(self,irida_connector):
		self.irida_connector=irida_connector

	def _get_rel_from_links(self, rel, links):
		href=None
	
		for l in links:
			if (l['rel'] == rel):
				href=l['href']
	
		if (href is None):
			raise Exception("Could not get rel="+rel+" from links")
		else:
			return href

	def _has_rel_in_links(self, rel, links):
		for l in links:
			if (l['rel'] == rel):
				return True
		return False

	def _log_json(self,json_obj):
		logger.log(LOGLEVEL_TRACE,json.dumps(json_obj, sort_keys=True, separators=(',',':'), indent=4))

	def _get_sistr_predictions(self, sistr_analysis_href):
		sistr_pred_json=None
	
		analysis=self.irida_connector.get(sistr_analysis_href)
	
		sistr_href=self._get_rel_from_links('outputFile/sistr-predictions', analysis['links'])
		sistr_pred=self.irida_connector.get_file(sistr_href)
		try:
			sistr_pred_json=sistr_pred.json()
		except json.decoder.JSONDecodeError as e:
			raise SistrResultsException("Error parsing JSON") from e
	
		if (sistr_pred_json is None):
			raise SistrResultsException("Could not get SISTR predictions for sistr " + sistr_analysis_href)

		self._log_json(sistr_pred_json)
	
		return sistr_pred_json

	def _has_sample_in_paired(self, paired_json):
		if (len(paired_json) > 0 and paired_json[0]['links'] is not None):
			return self._has_rel_in_links('sample',paired_json[0]['links'])
		else:
			return False

	def _get_sample_from_paired(self, paired_json):
		sample = None
	
		links=paired_json[0]['links']
		sample_href=self._get_rel_from_links('sample',links)
		sample = self.irida_connector.get(sample_href)
	
		if sample is None:
			raise Exception("Could not get sample corresponding to " + paired_path)
		else:
			return sample
	
	def get_user_project(self,project_id):
		"""Gets information on a particular IRIDA project

		Args:
		    project_id: The id of the project to search.

		Returns:  The JSON results for the IRIDA project
		"""
		return self.irida_connector.get('/api/projects/'+str(project_id))

	def get_user_projects(self):
		"""Gets information on all projects in IRIDA the current user has access to.

		Returns:  The JSON results for all the user-accessible projects in IRIDA.
		"""
		return self.irida_connector.get_resources('/api/projects')
	
	def get_sistr_results_for_project(self, project):
		"""Gets information on all SISTR results in a project (that is, automated SISTR results).
		   This is structured as a list of objects (on per sample) containing a SampleSistrInfo object if available and whether 
		   or not these results are available for a sample (from keys 'has_results').

		Args:
		    project:  The project to search through.

		Returns: A list of dictionaries containing SampleSistrInfo objects and/or indicators for missing results.
		"""
		sistr_results=[]
	
		sistr_results_for_project=self.irida_connector.get_resources('/api/projects/'+str(project)+'/samples')
	
		for sample in sistr_results_for_project:
			sample_pairs=self.irida_connector.get_resources('/api/samples/'+sample['identifier']+'/pairs')

			if len(sample_pairs) == 0:
				sistr_info = SampleSistrInfo({'sample': sample,
						'has_results': False
						})
			else:
				sistr_info = None
				for sequencing_object in sample_pairs:
					if (self._has_rel_in_links('analysis/sistr', sequencing_object['links'])):
						sistr_rel=self._get_rel_from_links('analysis/sistr', sequencing_object['links'])
	
						sistr=self.irida_connector.get(sistr_rel)
						
						if (sistr['analysisState'] != 'COMPLETED'):
							logger.warning("Skipping automated SISTR results associated with sample="+sample['sampleName']+" as state is not 'COMPLETED'.")
							if sistr_info is None:
								sistr_info = SampleSistrInfo({'sample': sample,
									'paired_files': sequencing_object,
									'has_results': False
									})
						else:
							sistr_info_curr=self.get_sistr_info_from_submission(sistr)
							if (sistr_info is None):
								sistr_info = sistr_info_curr
							elif sistr_info_curr.get_qc_status() == 'PASS' and (not sistr_info.has_sistr_results() or sistr_info.get_qc_status() != 'PASS'):
								sistr_info = sistr_info_curr
							elif sistr_info_curr.get_qc_status() == 'PASS' and (sistr_info_curr.get_submission_created_date() > sistr_info.get_submission_created_date()):
								sistr_info = sistr_info_curr
					elif sistr_info is None:
						sistr_info = SampleSistrInfo({'sample': sample,
								'paired_files': sequencing_object,
								'has_results': False
								})

			sistr_results.append(sistr_info)
		return sistr_results
		
	def get_sistr_info_from_submission(self, submission):
		"""Gets the relevent SISTR information from an IRIDA SISTR AnalysisSubmission.

		Args:
		    submission The IRIDA SISTR AnalysisSubmission data structure.

		Returns: The SISTR information object (SampleSistrInfo) fro this submission.
		"""
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
		sistr_info['sistr_predictions'] = self._get_sistr_predictions(sistr_analysis_href)
		sistr_info['has_results'] = True
		if (self._has_sample_in_paired(paired)):
			sistr_info['sample'] = self._get_sample_from_paired(paired)
		else:
			sistr_info['sample']=None
		sistr_info['submission'] = submission
	
		return SampleSistrInfo(sistr_info)
	
	def get_sistr_submissions_for_user(self):
		"""Gets all SISTR results accessible by a user (includes those submitted by a user or shared with a user via a project).

		Returns:  A list of SampleSistrInfo objects that the current user has access to.
		"""
		sistr_submissions_for_user=self.irida_connector.get_resources('/api/analysisSubmissions/analysisType/sistr')
		
		sistr_analysis_list=[]
		for sistr in sistr_submissions_for_user:
			try:
				if (sistr['analysisState'] == 'COMPLETED'):
					sistr_analysis_list.append(self.get_sistr_info_from_submission(sistr))
				else:
					logger.debug('Skipping incompleted sistr submission [id='+sistr['identifier']+']')
			except (HTTPError, SistrResultsException) as e:
				logger.error('Could not read information for SISTR analysis submission '+str(sistr)+ ', ignoring these results. Error: '+str(e))

		return sistr_analysis_list

