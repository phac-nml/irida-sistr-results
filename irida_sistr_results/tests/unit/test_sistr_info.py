import unittest

from irida_sistr_results.sistr_info import SampleSistrInfo


class SistrInfoTest(unittest.TestCase):

    def setUp(self):
        self.reportable_serovars = [
            'serovar1',
            'serovar2',
            'serovar3',
        ]

        self.sistr_info1 = {
            'sistr_predictions': [{
                'serovar': 'serovar1',
                'qc_status': 'PASS'
            }],
            'has_results': True
        }

        self.sistr_info1_fail_qc = {
            'sistr_predictions': [{
                'serovar': 'serovar1',
                'qc_status': 'FAIL'
            }],
            'has_results': True
        }

        self.sistr_info1_warn_qc = {
            'sistr_predictions': [{
                'serovar': 'serovar1',
                'qc_status': 'WARNING'
            }],
            'has_results': True
        }

        self.sistr_info4 = {
            'sistr_predictions': [{
                'serovar': 'serovar4',
                'qc_status': 'PASS'
            }],
            'has_results': True
        }

    def test_reportable_serovar_status_success(self):
        info = SampleSistrInfo(self.sistr_info1, self.reportable_serovars)

        self.assertTrue(info.is_reportable_serovar())
        self.assertEqual('PASS', info.get_reportable_serovar_status())
        self.assertEqual(1, info.get_reportable_status_numerical())

    def test_reportable_serovar_status_fail_qc(self):
        info = SampleSistrInfo(self.sistr_info1_fail_qc, self.reportable_serovars)

        self.assertFalse(info.is_reportable_serovar())
        self.assertEqual('FAIL', info.get_reportable_serovar_status())
        self.assertEqual(0, info.get_reportable_status_numerical())

    def test_reportable_serovar_status_warn_qc(self):
        info = SampleSistrInfo(self.sistr_info1_warn_qc, self.reportable_serovars)

        self.assertFalse(info.is_reportable_serovar())
        self.assertEqual('FAIL', info.get_reportable_serovar_status())
        self.assertEqual(0, info.get_reportable_status_numerical())

    def test_reportable_serovar_status_missing(self):
        info = SampleSistrInfo.create_empty_info(None, self.reportable_serovars)

        self.assertFalse(info.is_reportable_serovar())
        self.assertEqual('FAIL', info.get_reportable_serovar_status())
        self.assertEqual(0, info.get_reportable_status_numerical())

    def test_reportable_serovar_status_fail(self):
        info = SampleSistrInfo(self.sistr_info4, self.reportable_serovars)

        self.assertFalse(info.is_reportable_serovar())
        self.assertEqual('FAIL', info.get_reportable_serovar_status())
        self.assertEqual(0, info.get_reportable_status_numerical())
