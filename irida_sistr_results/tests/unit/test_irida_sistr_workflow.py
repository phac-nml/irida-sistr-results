import unittest

from irida_sistr_results.irida_sistr_workflow import IridaSistrWorkflow


class IridaSistrWorkflowTest(unittest.TestCase):

    def test_workflow_ids_or_versions_to_ids_version(self):
        ids = IridaSistrWorkflow.workflow_ids_or_versions_to_ids(['0.1'])

        self.assertEqual(['e559af58-a560-4bbd-997e-808bfbe026e2'], ids, "Invalid ids")

    def test_workflow_ids_or_versions_to_ids_id(self):
        ids = IridaSistrWorkflow.workflow_ids_or_versions_to_ids(['e559af58-a560-4bbd-997e-808bfbe026e2'])

        self.assertEqual(['e559af58-a560-4bbd-997e-808bfbe026e2'], ids, "Invalid ids")

    def test_workflow_ids_or_versions_to_ids_id_and_version(self):
        ids = IridaSistrWorkflow.workflow_ids_or_versions_to_ids(['e559af58-a560-4bbd-997e-808bfbe026e2', '0.2'])

        self.assertEqual(['e559af58-a560-4bbd-997e-808bfbe026e2', 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7'], ids,
                         "Invalid ids")

    def test_workflow_ids_or_versions_to_ids_invalid_version(self):
        self.assertRaises(KeyError, IridaSistrWorkflow.workflow_ids_or_versions_to_ids, ['0.1x'])

    def test_workflow_ids_or_versions_to_ids_invalid_id(self):
        self.assertRaises(KeyError, IridaSistrWorkflow.workflow_ids_or_versions_to_ids,
                          ['Xe8f9cc61-3264-48c6-81d9-02d9e84bccc7'])
