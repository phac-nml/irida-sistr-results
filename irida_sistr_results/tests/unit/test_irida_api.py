import unittest
from unittest.mock import patch
from unittest.mock import Mock

from irida_sistr_results.irida_api import IridaAPI

class IridaAPITest(unittest.TestCase):

    def setUp(self):
        self.connector = Mock()
        self.connector.get_resources = Mock()
        self.irida_api = IridaAPI(self.connector)
        self.irida_api.get_sistr_info_from_submission = Mock(side_effect=lambda x: x['identifier'])

    def _create_user_results(self, analysis_states):
        return [{
            'analysisState': state,
            'workflowId': '92ecf046-ee09-4271-b849-7a82625d6b60',
            'identifier': index,
            'name': 'sistr1'
        } for index, state in enumerate(analysis_states)]

    def test_get_sistr_submissions_for_user_single(self):
        self.connector.get_resources.return_value = self._create_user_results(['COMPLETED'])

        sistr_results = self.irida_api.get_sistr_submissions_for_user()

        self.assertEqual([0], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_user_multiple(self):
        self.connector.get_resources.return_value = self._create_user_results(['COMPLETED', 'COMPLETED'])

        sistr_results = self.irida_api.get_sistr_submissions_for_user()

        self.assertEqual([0,1], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_user_error(self):
        self.connector.get_resources.return_value = self._create_user_results(['ERROR'])

        sistr_results = self.irida_api.get_sistr_submissions_for_user()

        self.assertEqual(0, len(sistr_results), "Should have empty results")

    def test_get_sistr_submissions_for_user_error_one_success(self):
        self.connector.get_resources.return_value = self._create_user_results(['COMPLETED', 'ERROR'])

        sistr_results = self.irida_api.get_sistr_submissions_for_user()

        self.assertEqual([0], sistr_results, "Should have empty results")

