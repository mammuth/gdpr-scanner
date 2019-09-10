import os
import unittest

from analyzer.analyze import Analyzer
from analyzer.checks.privacy_statement_missing import PrivacyStatementMissingCheck
from analyzer.checks.tracking_service_ip_not_anonymized import TrackingServiceIPNotAnonymized


class MetricChecksTestCase(unittest.TestCase):

    def setUp(self) -> None:
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        self.analyzer = Analyzer(crawler_metadata_filepath=os.path.join(tests_dir, 'test-output/crawler.json'))  # We're calling the checks manually, we just need the analyzer for the crawler meta data  # noqa

    def test_privacy_statement_missing(self):
        check = PrivacyStatementMissingCheck(self.analyzer, 'lupus-ddns.de')
        result = check.check()
        self.assertEqual(result.passed, True)

    def test_tracking_service_ip_not_anonymized(self):
        check = TrackingServiceIPNotAnonymized(self.analyzer, 'lupus-ddns.de')
        result = check.check()
        self.assertEqual(result.passed, True, 'GA Anonymized IP was not detected correctly')

        check = TrackingServiceIPNotAnonymized(self.analyzer, 'lupus-ddns.de')
        result = check.check()
        self.assertEqual(result.passed, True, 'Missing anonymized IP was not detected correctly')


if __name__ == '__main__':
    unittest.main()
