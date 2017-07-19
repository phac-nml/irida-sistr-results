class SampleSistrInfo(object):

	def __init__(self, sistr_info):
		self.sistr_info = sistr_info

	def has_sistr_results(self):
		return self.sistr_info['has_results']

	def get_sample_name(self):
		return self.sistr_info['sample']['sampleName']

	def get_serovar(self):
		return self.sistr_info['sistr_predictions'][0]['serovar']

	def get_serovar_antigen(self):
		return self.sistr_info['sistr_predictions'][0]['serovar_antigen']

	def get_serovar_cgmlst(self):
		serovar_cgmlst=self.sistr_info['sistr_predictions'][0]['serovar_cgmlst']
		if (serovar_cgmlst is None):
			return 'None'
		else:
			return serovar_cgmlst

	def get_qc_status(self):
		return self.sistr_info['sistr_predictions'][0]['qc_status']

	def get_qc_messages(self):
		return self.sistr_info['sistr_predictions'][0]['qc_messages']

	def get_submission_url(self, irida_base_url):
		submission_identifier=self.sistr_info['submission']['identifier']
		submission_url=irida_base_url
		if submission_url.endswith('/'):
			submission_url += 'analysis/'
		else:
			submission_url += '/analysis/'
		submission_url += submission_identifier

		return submission_url

	def get_sample_id(self):
		return self.sistr_info['sample']['identifier']

	def get_paired_id(self):
		return self.sistr_info['paired_files'][0]['identifier']
