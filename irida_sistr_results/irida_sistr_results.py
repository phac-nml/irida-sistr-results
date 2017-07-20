import logging
from datetime import datetime

class IridaSistrResults(object):

	def __init__(self,irida_api,include_user_results,update_existing_with_user_results):
		self.irida_api=irida_api
		self.include_user_results=include_user_results
		self.update_existing_with_user_results=update_existing_with_user_results

	def get_sistr_results(self,project):
		sistr_results={}
		project_results=self.irida_api.get_sistr_results_for_project(project)

		for result in project_results:
			sample_id=result.get_sample_id()
			sistr_results[sample_id]=result

		if self.include_user_results:
			user_results=self.irida_api.get_sistr_submissions_for_user()
			for result in user_results:
				sample_id=result.get_sample_id()
	
				if (sample_id in sistr_results and result.has_sistr_results()):
					if (self.update_existing_with_user_results):
						if (sistr_results[sample_id].get_submission_created_date() < result.get_submission_created_date()):
							logging.info(self._result_to_sample_log_string(sistr_results[sample_id], result, "older")+" Updating.")
							sistr_results[sample_id] = result
						else:
							logging.info(self._result_to_sample_log_string(sistr_results[sample_id], result, "newer")+" Not updating.")
					else:
						logging.info("Found result for sample="+result.get_sample_name() + " for user. Will not replace with exisiting result.")
				else:
					sistr_results[sample_id]=result

		return sistr_results

	def _timef(self,timestamp):
		return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

	def _result_to_sample_log_string(self,r1,r2,word):
		return "Sample [name="+r1.get_sample_name()+", id="+str(r1.get_sample_id())+"] has exisiting analysis [id="+r1.get_submission_identifier()+", created_date="+self._timef(r1.get_submission_created_date())+"] "+word+" than analysis [id="+r2.get_submission_identifier()+", created_date="+self._timef(r2.get_submission_created_date())+"]."
