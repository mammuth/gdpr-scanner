import os
import unittest

from analyzer.checks import CheckResultPassed
from analyzer.checks.metrics.privacy_missing_third_party import PrivacyMissingGoogleAnalyticsCheck
from analyzer.checks.metrics.privacy_statement_missing import PrivacyStatementMissingCheck
from analyzer.checks.metrics.tracking_service_ip_not_anonymized import GoogleAnalyticsIPNotAnonymizedCheck


class BaseMetricCheckTestCase:

    def setUp(self) -> None:  # noqa
        from analyzer.analyze import Analyzer
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        # Analyzer is only used for getting the meta data in the correct format.
        # Afterwards we're calling the check classes directly
        analyzer = Analyzer(crawler_metadata_filepath=os.path.join(tests_dir, 'test-output/crawler.json'))
        self.metadata = analyzer.crawler_meta_data
        self.metadata_filepath = analyzer.crawler_metadata_filepath


class PrivacyStatementMissingTestCase(BaseMetricCheckTestCase, unittest.TestCase):

    def test_missing_privacy_statement_detected(self):
        domain = 'goldmarie-friends.de'  # has no privacy statement
        check = PrivacyStatementMissingCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.FAILED)

    def test_present_privacy_statement_detected(self):
        domain = 'lupus-ddns.de'  # has privacy statement
        check = PrivacyStatementMissingCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.PASSED)


class GoogleAnalyticsIPAnonymizationTestCase(BaseMetricCheckTestCase, unittest.TestCase):

    def test_ga_without_anonymiziation(self):
        domain = 'kristalltherme-altenau.de'  # has GA, but no anonymization
        check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.FAILED, 'Missing anonymized IP was not detected')

    def test_ga_with_anonymization(self):
        domain = 'lupus-ddns.de'
        check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.PASSED)

    def test_gtag_without_anonymization(self):
        # ToDo: Test: gtag without anonymization
        pass

    def test_gtag_with_anonymization(self):
        domain = 'goldmarie-friends.de'
        check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.PASSED)

    def test_legacy_ga_without_anonymization(self):
        domain = 'officecoach24.de'  # Legacy analytics without anonymize
        check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.FAILED)

    def test_legacy_ga_with_anonymization(self):
        pass
        # ToDo: Test: Legacy analytics with anonymize
        # domain = ''  # Legacy analytics with anonymize
        # check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        # result = check.check()
        # self.assertEqual(result.passed, CheckResultPassed.PASSED, 'Lgecy GA Anonymized IP was not detected')

    def test_domain_without_google_analytics(self):
        domain = 'logbuch-netzpolitik.de'  # has no GA at all
        check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.PASSED)


class PrivacyMissingGAMentionTestCase(BaseMetricCheckTestCase, unittest.TestCase):

    def test_ga_used_without_mention(self):
        domain = 'berufskleidung24.de'
        check = PrivacyMissingGoogleAnalyticsCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.FAILED)

    def test_ga_used_with_mention(self):
        domain = 'lupus-ddns.de'
        check = PrivacyMissingGoogleAnalyticsCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.PASSED)

    def test_ga_used_no_privacy_policy(self):
        domain = 'goldmarie-friends.de'
        check = PrivacyMissingGoogleAnalyticsCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.FAILED)

    def test_ga_not_used(self):
        domain = 'logbuch-netzpolitik.de'
        check = PrivacyMissingGoogleAnalyticsCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResultPassed.UNCERTAIN)
        self.assertEqual(result.passed.passed, True)


if __name__ == '__main__':
    unittest.main()
