import unittest
from unittest.mock import Mock

from irida_sistr_results.irida_sistr_results import IridaSistrResults
from irida_sistr_results.sistr_info import SampleSistrInfo


class IridaSistrResultsTest(unittest.TestCase):

    def setUp(self):
        self.irida_api = Mock()
        self.irida_sistr_results = IridaSistrResults(self.irida_api, False, True)

    def _create_sistr_info(self, workflow_id, qc_status, created_date, sample_id):
        return SampleSistrInfo({
            'submission': {
                'workflowId': workflow_id,
                'createdDate': created_date,
                'identifier': '1'
            },
            'has_results': True,
            'sistr_predictions': [{
                'qc_status': qc_status
            }],
            'sample': {
                'identifier': str(sample_id),
                'sampleName': 'name' + str(sample_id)
            }
        }, [])

    def _create_project_sistr_results(self, workflow_id, sample_ids):
        return [self._create_sistr_info(workflow_id, 'PASS', 1500000000001, sample_id) for sample_id in sample_ids]

    def _create_project_info(self, id):
        return {
            'identifier': str(id),
            'name': 'project' + str(id),
        }

    def test_get_sistr_results_from_projects(self):
        project_sistr_results = self._create_project_sistr_results('92ecf046-ee09-4271-b849-7a82625d6b60', [1, 2])
        expected_results1 = project_sistr_results[0]
        expected_results2 = project_sistr_results[1]

        self.irida_api.get_user_project = Mock(return_value=self._create_project_info(1))
        self.irida_api.get_sistr_results_for_project = Mock(return_value=project_sistr_results)
        self.irida_api.get_sistr_submissions_shared_to_project = Mock(return_value=[])

        results = self.irida_sistr_results.get_sistr_results_from_projects([1])

        self.assertEqual(results, {'1': {'1': expected_results1, '2': expected_results2}},
                         "Did not get expected SISTR results")

    def test_get_sistr_results_from_projects_update_from_shared_date(self):
        project_sistr_results = self._create_project_sistr_results('92ecf046-ee09-4271-b849-7a82625d6b60', [1])
        shared_results = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000002, 1)
        expected_results = shared_results

        self.irida_api.get_user_project = Mock(return_value=self._create_project_info(1))
        self.irida_api.get_sistr_results_for_project = Mock(return_value=project_sistr_results)
        self.irida_api.get_sistr_submissions_shared_to_project = Mock(return_value=[shared_results])

        results = self.irida_sistr_results.get_sistr_results_from_projects([1])

        self.assertEqual(results, {'1': {'1': expected_results}}, "Did not get expected SISTR results")

    def test_get_sistr_results_from_projects_update_from_shared_fail(self):
        project_sistr_results = self._create_project_sistr_results('92ecf046-ee09-4271-b849-7a82625d6b60', [1])
        shared_results = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'FAIL', 1500000000002, 1)
        expected_results = shared_results

        self.irida_api.get_user_project = Mock(return_value=self._create_project_info(1))
        self.irida_api.get_sistr_results_for_project = Mock(return_value=project_sistr_results)
        self.irida_api.get_sistr_submissions_shared_to_project = Mock(return_value=[shared_results])

        results = self.irida_sistr_results.get_sistr_results_from_projects([1])

        self.assertEqual(results, {'1': {'1': expected_results}}, "Did not get expected SISTR results")

    def test_get_sistr_results_from_projects_no_update_from_shared_date(self):
        project_sistr_results = self._create_project_sistr_results('92ecf046-ee09-4271-b849-7a82625d6b60', [1])
        shared_results = self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000000, 1)
        expected_results = project_sistr_results[0]

        self.irida_api.get_user_project = Mock(return_value=self._create_project_info(1))
        self.irida_api.get_sistr_results_for_project = Mock(return_value=project_sistr_results)
        self.irida_api.get_sistr_submissions_shared_to_project = Mock(return_value=[shared_results])

        results = self.irida_sistr_results.get_sistr_results_from_projects([1])

        self.assertEqual(results, {'1': {'1': expected_results}}, "Did not get expected SISTR results")

    def test_get_sistr_results_from_projects_multipleshared_update_pass(self):
        project_sistr_results = self._create_project_sistr_results('92ecf046-ee09-4271-b849-7a82625d6b60', [1])
        shared_results = [
            self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'FAIL', 1500000000002, 1),
            self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000003, 1)
        ]
        expected_results = shared_results[1]

        self.irida_api.get_user_project = Mock(return_value=self._create_project_info(1))
        self.irida_api.get_sistr_results_for_project = Mock(return_value=project_sistr_results)
        self.irida_api.get_sistr_submissions_shared_to_project = Mock(return_value=shared_results)

        results = self.irida_sistr_results.get_sistr_results_from_projects([1])

        self.assertEqual(results, {'1': {'1': expected_results}}, "Did not get expected SISTR results")

    def test_get_sistr_results_from_projects_multipleshared_update_fail_switch_order(self):
        project_sistr_results = self._create_project_sistr_results('92ecf046-ee09-4271-b849-7a82625d6b60', [1])
        shared_results = [
            self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'PASS', 1500000000002, 1),
            self._create_sistr_info('92ecf046-ee09-4271-b849-7a82625d6b60', 'FAIL', 1500000000003, 1)
        ]
        expected_results = shared_results[1]

        self.irida_api.get_user_project = Mock(return_value=self._create_project_info(1))
        self.irida_api.get_sistr_results_for_project = Mock(return_value=project_sistr_results)
        self.irida_api.get_sistr_submissions_shared_to_project = Mock(return_value=shared_results)

        results = self.irida_sistr_results.get_sistr_results_from_projects([1])

        self.assertEqual(results, {'1': {'1': expected_results}}, "Did not get expected SISTR results")
