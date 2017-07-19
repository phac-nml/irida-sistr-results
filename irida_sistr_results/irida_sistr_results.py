import logging

class IridaSistrResults(object):

	def __init__(self,irida_api):
		self.irida_api=irida_api

	def get_sistr_results(self,project):
		sistr_results={}
		project_results=self.irida_api.get_sistr_results_for_project(project)

		for result in project_results:
			sample_id=result.get_sample_id()
			sistr_results[sample_id]=result

		user_results=self.irida_api.get_sistr_submissions_for_user()

		for result in user_results:
			sample_id=result.get_sample_id()

			if (sample_id in sistr_results and result.has_sistr_results()):
				logging.warn("sample_name="+result.get_sample_name()+", sample_id="+str(sample_id)+" already has SISTR results, will not update")
			else:
				sistr_results[sample_id]=result

		return sistr_results

