import os
import unittest

from analyzer.checks.privacy_statement_missing import PrivacyStatementMissingCheck
from analyzer.checks.tracking_service_ip_not_anonymized import TrackingServiceIPNotAnonymizedCheck


class MetricChecksTestCase(unittest.TestCase):
    # ToDo: Reduce test-output/ file size (only include the domains we test here)

    def setUp(self) -> None:
        from analyzer.analyze import Analyzer
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        # Analyzer is only used for getting the meta data in the correct format.
        # Afterwards we're calling the check classes directly
        analyzer = Analyzer(crawler_metadata_filepath=os.path.join(tests_dir, 'test-output/crawler.json'))
        self.metadata = analyzer.crawler_meta_data
        self.metadata_filepath = analyzer.crawler_metadata_filepath

    def test_privacy_statement_missing(self):
        domain = 'lupus-ddns.de'  # has privacy statement
        check = PrivacyStatementMissingCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, True, 'Present privacy statement was not detected')

        domain = 'goldmarie-friends.de'  # has no privacy statement
        check = PrivacyStatementMissingCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, False, 'Missing privacy statement was not detected')

    def test_tracking_service_ip_not_anonymized(self):
        domain = 'lupus-ddns.de'
        check = TrackingServiceIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, True, 'GA Anonymized IP was not detected')

        domain = 'goldmarie-friends.de'
        check = TrackingServiceIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, True, 'GTag anonymized IP was not detected')

        domain = 'officecoach24.de'  # Legacy analytics without anonymize
        check = TrackingServiceIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, False, 'Missing anonymized IP was not detected with legacy GA')

        # ToDo Legacy analytics with anonymize
        # domain = ''  # Legacy analytics with anonymize
        # check = TrackingServiceIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        # result = check.check()
        # self.assertEqual(result.passed, True, 'Lgecy GA Anonymized IP was not detected')

        domain = 'logbuch-netzpolitik.de'  # has no GA at all
        check = TrackingServiceIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, True, 'Page without GA was flagged as missing anonymized IP')

        domain = 'kristalltherme-altenau.de'  # has GA, but no anonymization
        check = TrackingServiceIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, False, 'Missing anonymized IP was not detected')


if __name__ == '__main__':
    unittest.main()
