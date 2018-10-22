from datetime import datetime

from irida_sistr_results.irida_sistr_workflow import IridaSistrWorkflow


class SampleSistrInfo(object):
    """Stores and provides access to SISTR/IRIDA information for a particular sample."""

    def __init__(self, sistr_info, reportable_serovars):
        self.sistr_info = sistr_info
        self.reportable_serovars = reportable_serovars

    @classmethod
    def create_empty_info(cls, sample, sequencing_object=None):
        """
        Creates an empty SampleSistrInfo object (no SISTR results).
        :param sample: The sample this object refers to.
        :param sequencing_object: The sequencing object (default None).
        :return: An empty SampleSistrInfo.
        """
        data = {'sample': sample,
                'has_results': False
                }

        if sequencing_object is not None:
            data['paired_files'] = sequencing_object

        reportable_serovars = []

        return cls(data, reportable_serovars)

    def has_sistr_results(self):
        return self.sistr_info['has_results']

    def get_sample_name(self):
        if (self.sistr_info['sample'] is not None):
            return self.sistr_info['sample']['sampleName']
        else:
            return "N/A"

    def _get_sistr(self):
        return self.sistr_info['sistr_predictions'][0]

    def get_serovar(self):
        return self._get_sistr()['serovar']

    def get_serovar_antigen(self):
        return self._get_sistr()['serovar_antigen']

    def get_serovar_cgmlst(self):
        serovar_cgmlst = self._get_sistr()['serovar_cgmlst']
        if (serovar_cgmlst is None):
            return ''
        else:
            return serovar_cgmlst

    def get_reportable_serovar_status(self):
        if self.has_sistr_results() and self.is_qc_pass() and self.get_serovar() in self.reportable_serovars:
            return 'PASS'
        else:
            return 'FAIL'

    def is_reportable_serovar(self):
        return self.get_reportable_serovar_status() == 'PASS'

    def get_reportable_status_numerical(self):
        """Gets numerical value of reportable status, used for sorting"""
        return ['FAIL', 'PASS'].index(self.get_reportable_serovar_status())

    def get_serogroup(self):
        return self._get_sistr()['serogroup']

    def get_h1(self):
        return self._get_sistr()['h1']

    def get_h2(self):
        return self._get_sistr()['h2']

    def get_o_antigen(self):
        return self._get_sistr()['o_antigen']

    def is_qc_pass(self):
        return self.get_qc_status() == 'PASS'

    def get_qc_status(self):
        return 'MISSING' if (not self.has_sistr_results()) else self._get_sistr()['qc_status']

    def get_qc_status_numerical(self):
        """Gets numerical value for QC status, used for sorting"""
        return ['MISSING', 'FAIL', 'WARNING', 'PASS'].index(self.get_qc_status())

    def get_qc_messages(self):
        return self._get_sistr()['qc_messages']

    def get_cgmlst_subspecies(self):
        return self._get_sistr()['cgmlst_subspecies']

    def get_cgmlst_genome(self):
        return self._get_sistr()['cgmlst_genome_match']

    def get_cgmlst_matching_alleles(self):
        return self._get_sistr()['cgmlst_matching_alleles']

    def get_cgmlst_matching_total_alleles(self):
        return str(self.get_cgmlst_matching_alleles()) + '/330'

    def get_cgmlst_matching_proportion(self):
        return float(self.get_cgmlst_matching_alleles()) / 330

    def get_cgmlst_sequence_type(self):
        return self._get_sistr()['cgmlst_ST']

    def get_mash_subspecies(self):
        return self._get_sistr()['mash_subspecies']

    def get_mash_serovar(self):
        return self._get_sistr()['mash_serovar']

    def get_mash_genome(self):
        return self._get_sistr()['mash_genome']

    def get_mash_distance(self):
        return self._get_sistr()['mash_distance']

    def get_submission_url(self, irida_base_url):
        submission_url = irida_base_url
        if submission_url.endswith('/'):
            submission_url += 'analysis/'
        else:
            submission_url += '/analysis/'
        submission_url += self.get_submission_identifier()

        return submission_url

    def get_submission_identifier(self):
        return self.sistr_info['submission']['identifier']

    def get_submission_workflow_id(self):
        return self.sistr_info['submission']['workflowId']

    def get_submission_workflow_version(self):
        return IridaSistrWorkflow.workflow_id_to_version(self.get_submission_workflow_id())

    def get_submission_created_date(self):
        return datetime.fromtimestamp(self.sistr_info['submission']['createdDate'] / 1000)

    def get_sample_created_date(self):
        if (self.sistr_info['sample'] is not None):
            return datetime.fromtimestamp(self.sistr_info['sample']['createdDate'] / 1000)
        else:
            return "N/A"

    def get_sample_id(self):
        if (self.sistr_info['sample'] is not None):
            return self.sistr_info['sample']['identifier']
        else:
            return "N/A"

    def get_paired_id(self):
        return self.sistr_info['paired_files'][0]['identifier']
