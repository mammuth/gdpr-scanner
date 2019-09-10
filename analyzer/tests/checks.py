import os
import unittest

from analyzer.checks.privacy_statement_missing import PrivacyStatementMissingCheck
from analyzer.checks.tracking_service_ip_not_anonymized import TrackingServiceIPNotAnonymizedCheck


class MetricChecksTestCase(unittest.TestCase):
    # ToDo: Reduce test-output size (only include the stuff we test here)

    def setUp(self) -> None:
        from analyzer.analyze import Analyzer
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        # Analyzer is only used for getting the meta data in the correct format.
        # Afterwards we're calling the check classes directly
        analyzer = Analyzer(crawler_metadata_filepath=os.path.join(tests_dir, 'test-output/crawler.json'))
        self.metadata = analyzer.crawler_meta_data
        self.metadata_filepath = analyzer.crawler_metadata_filepath

    def test_privacy_statement_missing(self):
        domain = 'lupus-ddns.de'
        check = PrivacyStatementMissingCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, True)

    def test_tracking_service_ip_not_anonymized(self):
        domain = 'lupus-ddns.de'
        check = TrackingServiceIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, True, 'GA Anonymized IP was not detected correctly')

        domain = 'lupus-ddns.de'
        check = TrackingServiceIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, True, 'Missing anonymized IP was not detected correctly')


if __name__ == '__main__':
    unittest.main()
