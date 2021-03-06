import unittest
from unittest.mock import Mock

from irida_sistr_results.irida_api import IridaAPI
from irida_sistr_results.sistr_info import SampleSistrInfo


class IridaAPITest(unittest.TestCase):

    def setUp(self):
        self.connector = Mock()
        self.connector.get_resources = Mock()
        self.irida_api = IridaAPI(self.connector, [])
        self.irida_api.get_sistr_info_from_submission = Mock(side_effect=lambda x: x['identifier'])
        self.irida_api._get_sistr_submission = Mock(side_effect=lambda x: {'identifier': x})

    def _create_user_results_state(self, analysis_states):
        return [{
            'analysisState': state,
            'workflowId': '92ecf046-ee09-4271-b849-7a82625d6b60',
            'identifier': index,
            'name': 'sistr'
        } for index, state in enumerate(analysis_states)]

    def _create_user_results_workflow(self, workflow_ids):
        return [{
            'analysisState': 'COMPLETED',
            'workflowId': workflow,
            'identifier': index,
            'name': 'sistr'
        } for index, workflow in enumerate(workflow_ids)]

    def _create_sistr_info(self, workflow_id, qc_status, created_date):
        return SampleSistrInfo({
            'submission': {
                'workflowId': workflow_id,
                'createdDate': created_date
            },
            'has_results': True,
            'sistr_predictions': [{
                'qc_status': qc_status
            }],
            'sample': {
                'identifier': '1',
            }
        }, [])

    def test_get_sistr_submissions_for_user_single(self):
        self.connector.get_resources.return_value = self._create_user_results_state(['COMPLETED'])
        sistr_results = self.irida_api.get_sistr_submissions_for_user()
        self.assertEqual([0], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_user_multiple(self):
        self.connector.get_resources.return_value = self._create_user_results_state(['COMPLETED', 'COMPLETED'])
        sistr_results = self.irida_api.get_sistr_submissions_for_user()
        self.assertEqual([0, 1], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_user_error(self):
        self.connector.get_resources.return_value = self._create_user_results_state(['ERROR'])
        sistr_results = self.irida_api.get_sistr_submissions_for_user()
        self.assertEqual([], sistr_results, "Should have empty results")

    def test_get_sistr_submissions_for_user_error_one_success(self):
        self.connector.get_resources.return_value = self._create_user_results_state(['COMPLETED', 'ERROR'])
        sistr_results = self.irida_api.get_sistr_submissions_for_user()
        self.assertEqual([0], sistr_results, "Should have empty results")

    def test_get_sistr_submissions_for_user_default(self):
        self.connector.get_resources.return_value = self._create_user_results_workflow(
            ['92ecf046-ee09-4271-b849-7a82625d6b60', 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        sistr_results = self.irida_api.get_sistr_submissions_for_user()
        self.assertEqual([0, 1], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_user_one_workflow(self):
        self.connector.get_resources.return_value = self._create_user_results_workflow(
            ['92ecf046-ee09-4271-b849-7a82625d6b60', 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        sistr_results = self.irida_api.get_sistr_submissions_for_user(['92ecf046-ee09-4271-b849-7a82625d6b60'])
        self.assertEqual([0], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_user_other_workflow(self):
        self.connector.get_resources.return_value = self._create_user_results_workflow(
            ['92ecf046-ee09-4271-b849-7a82625d6b60', 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        sistr_results = self.irida_api.get_sistr_submissions_for_user(['e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        self.assertEqual([1], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_user_both_workflows(self):
        self.connector.get_resources.return_value = self._create_user_results_workflow(
            ['92ecf046-ee09-4271-b849-7a82625d6b60', 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        sistr_results = self.irida_api.get_sistr_submissions_for_user(['92ecf046-ee09-4271-b849-7a82625d6b60',
                                                                       'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        self.assertEqual([0, 1], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_project_multiple(self):
        self.connector.get_resources.return_value = self._create_user_results_state(['COMPLETED', 'COMPLETED'])
        sistr_results = self.irida_api.get_sistr_submissions_shared_to_project(1)
        self.assertEqual([0, 1], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_project_error_one_success(self):
        self.connector.get_resources.return_value = self._create_user_results_state(['COMPLETED', 'ERROR'])
        sistr_results = self.irida_api.get_sistr_submissions_shared_to_project(1)
        self.assertEqual([0], sistr_results, "Should have empty results")

    def test_get_sistr_submissions_for_project_one_workflow(self):
        self.connector.get_resources.return_value = self._create_user_results_workflow(
            ['92ecf046-ee09-4271-b849-7a82625d6b60', 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        sistr_results = self.irida_api.get_sistr_submissions_shared_to_project(1,
                                                                               ['92ecf046-ee09-4271-b849-7a82625d6b60'])
        self.assertEqual([0], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_project_other_workflow(self):
        self.connector.get_resources.return_value = self._create_user_results_workflow(
            ['92ecf046-ee09-4271-b849-7a82625d6b60', 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        sistr_results = self.irida_api.get_sistr_submissions_shared_to_project(1,
                                                                               ['e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        self.assertEqual([1], sistr_results, "Should have correct identifiers")

    def test_get_sistr_submissions_for_project_both_workflows(self):
        self.connector.get_resources.return_value = self._create_user_results_workflow(
            ['92ecf046-ee09-4271-b849-7a82625d6b60', 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        sistr_results = self.irida_api.get_sistr_submissions_shared_to_project(1,
                                                                               ['92ecf046-ee09-4271-b849-7a82625d6b60',
                                                                                'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        self.assertEqual([0, 1], sistr_results, "Should have correct identifiers")

    def test_update_sample_sistr_info_most_recent(self):
        curr_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        new_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000001)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info,
                                                                   ['92ecf046-ee09-4271-b849-7a82625d6b60'])
        self.assertEqual(new_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_skip_workflow(self):
        curr_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        new_sistr_info = self._create_sistr_info('e8f9cc61-3264-48c6-81d9-02d9e84bccc7', 'PASS', 1500000000001)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info,
                                                                   ['92ecf046-ee09-4271-b849-7a82625d6b60'])
        self.assertEqual(curr_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_use_most_recent_both_workflows(self):
        curr_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        new_sistr_info = self._create_sistr_info('e8f9cc61-3264-48c6-81d9-02d9e84bccc7', 'PASS', 1500000000001)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info,
                                                                   ['92ecf046-ee09-4271-b849-7a82625d6b60',
                                                                    'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        self.assertEqual(new_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_use_most_recent_all_workflows(self):
        curr_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        new_sistr_info = self._create_sistr_info('e8f9cc61-3264-48c6-81d9-02d9e84bccc7', 'PASS', 1500000000001)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info, None)
        self.assertEqual(new_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_equal_date(self):
        curr_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        new_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info,
                                                                   ['92ecf046-ee09-4271-b849-7a82625d6b60'])
        self.assertEqual(curr_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_pass(self):
        curr_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'FAIL', 1500000000000)
        new_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info,
                                                                   ['92ecf046-ee09-4271-b849-7a82625d6b60'])
        self.assertEqual(new_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_fail(self):
        curr_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        new_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'FAIL', 1500000000001)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info,
                                                                   ['92ecf046-ee09-4271-b849-7a82625d6b60'])
        self.assertEqual(curr_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_no_results(self):
        curr_sistr_info = SampleSistrInfo.create_empty_info({
            'sample': {
                'identifier': '1',
            }
        })
        new_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info, None)
        self.assertEqual(new_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_no_results_fail(self):
        curr_sistr_info = SampleSistrInfo.create_empty_info({
            'sample': {
                'identifier': '1',
            }
        })
        new_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'FAIL', 1500000000000)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info, None)
        self.assertEqual(new_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_no_results_workflow_id(self):
        curr_sistr_info = SampleSistrInfo.create_empty_info({
            'sample': {
                'identifier': '1',
            }
        })
        new_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info,
                                                                   ['92ecf046-ee09-4271-b849-7a82625d6b60'])
        self.assertEqual(new_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_no_results_workflow_id_fail(self):
        curr_sistr_info = SampleSistrInfo.create_empty_info({
            'sample': {
                'identifier': '1',
            }
        })
        new_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'FAIL', 1500000000000)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info,
                                                                   ['92ecf046-ee09-4271-b849-7a82625d6b60'])
        self.assertEqual(new_sistr_info, updated_results, "Did not update to proper results")

    def test_update_sample_sistr_info_no_results_workflow_id_incorrect(self):
        curr_sistr_info = SampleSistrInfo.create_empty_info({
            'sample': {
                'identifier': '1',
            }
        })
        new_sistr_info = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000)
        updated_results = self.irida_api._update_sample_sistr_info(curr_sistr_info, new_sistr_info,
                                                                   ['e8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
        self.assertEqual(curr_sistr_info, updated_results, "Did not update to proper results")
