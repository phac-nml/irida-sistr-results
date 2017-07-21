import logging
from datetime import datetime

class IridaSistrResults(object):

	def __init__(self,irida_api,include_user_results,update_existing_with_user_results):
		self.irida_api=irida_api
		self.include_user_results=include_user_results
		self.update_existing_with_user_results=update_existing_with_user_results
		self.sistr_results={}
		self.sample_project={}

	def get_sistr_results(self,projects):
		for p in projects:
			logging.debug("Working on project " + str(p))
			self._load_sistr_results_for_project(p)

		if (self.include_user_results):
			self._load_sistr_results_from_user()

		return self.sistr_results

	def _load_sistr_results_from_user(self):
		user_results=self.irida_api.get_sistr_submissions_for_user()
		for result in user_results:
			sample_id=result.get_sample_id()

			if (sample_id in self.sample_project and result.has_sistr_results()):
				for project in self.sample_project[sample_id]:
					sistr_results_project=self.sistr_results[project]
					if sample_id in sistr_results_project:
						if (not sistr_results_project[sample_id].has_sistr_results()):
							sistr_results_project[sample_id] = result
						elif (sistr_results_project[sample_id].get_submission_created_date() < result.get_submission_created_date()):
							if (self.update_existing_with_user_results):
								logging.info(self._result_to_sample_log_string(sistr_results_project[sample_id], result, "older")+" Updating.")
								sistr_results_project[sample_id] = result
							else:
								logging.info("Found result for sample="+result.get_sample_name() + " for user. Will not replace with exisiting result.")
						else:
							logging.info(self._result_to_sample_log_string(sistr_results_project[sample_id], result, "newer")+" Not updating.")

	def _load_sistr_results_for_project(self,project):
		if (project in self.sistr_results):
			raise Exception("Error: project " + str(project) + " already examined")
		
		self.sistr_results[project]={}
		project_results=self.irida_api.get_sistr_results_for_project(project)

		for result in project_results:
			sample_id=result.get_sample_id()
			self.sistr_results[project][sample_id]=result
			if (sample_id in self.sample_project):
				self.sample_project[sample_id].append(project)
			else:	
				self.sample_project[sample_id]=[project]

	def _timef(self,timestamp):
		return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

	def _result_to_sample_log_string(self,r1,r2,word):
		return "Sample [name="+r1.get_sample_name()+", id="+str(r1.get_sample_id())+"] has exisiting analysis [id="+r1.get_submission_identifier()+", created_date="+self._timef(r1.get_submission_created_date())+"] "+word+" than analysis [id="+r2.get_submission_identifier()+", created_date="+self._timef(r2.get_submission_created_date())+"]."
