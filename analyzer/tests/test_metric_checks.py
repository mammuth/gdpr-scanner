import os
import unittest

from analyzer.checks.check_result import CheckResult
from analyzer.checks.metrics.privacy_missing_third_party import PrivacyMissingGoogleAnalyticsCheck, \
    PrivacyMissingTwitterCheck, PrivacyMissingMatomoCheck, PrivacyMissingHubspotCheck, PrivacyMissingFacebookPixelCheck
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
        self.assertEqual(result.passed, CheckResult.PassType.FAILED)

    def test_present_privacy_statement_detected(self):
        domain = 'lupus-ddns.de'  # has privacy statement
        check = PrivacyStatementMissingCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PASSED)


class GoogleAnalyticsIPAnonymizationTestCase(BaseMetricCheckTestCase, unittest.TestCase):

    def test_ga_without_anonymiziation(self):
        domain = 'kristalltherme-altenau.de'  # has GA, but no anonymization
        check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.FAILED, 'Missing anonymized IP was not detected')

    def test_ga_with_anonymization(self):
        domain = 'lupus-ddns.de'
        check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PASSED)

    def test_gtag_with_anonymization(self):
        domain = 'goldmarie-friends.de'
        check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PASSED)

    def test_legacy_ga_without_anonymization(self):
        domain = 'officecoach24.de'  # Legacy analytics without anonymize
        check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.FAILED)

    def test_domain_without_google_analytics(self):
        domain = 'logbuch-netzpolitik.de'  # has no GA at all
        check = GoogleAnalyticsIPNotAnonymizedCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PASSED)


class PrivacyMissingGAMentionTestCase(BaseMetricCheckTestCase, unittest.TestCase):

    def test_ga_used_without_mention(self):
        domain = 'berufskleidung24.de'
        check = PrivacyMissingGoogleAnalyticsCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.FAILED)

    def test_ga_used_with_mention(self):
        domain = 'lupus-ddns.de'
        check = PrivacyMissingGoogleAnalyticsCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PASSED)

    def test_ga_used_no_privacy_policy(self):
        domain = 'goldmarie-friends.de'
        check = PrivacyMissingGoogleAnalyticsCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PRECONDITION_FAILED)

    def test_ga_not_used(self):
        domain = 'logbuch-netzpolitik.de'
        check = PrivacyMissingGoogleAnalyticsCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.NOT_APPLICABLE)
        self.assertEqual(result.passed.passed, True)


class PrivacyMissingTwitterMentionTestCase(BaseMetricCheckTestCase, unittest.TestCase):

    def test_twitter_used_no_privacy_policy(self):
        domain = 'officecoach24.de'
        check = PrivacyMissingTwitterCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PRECONDITION_FAILED)

    def test_twitter_not_used(self):
        domain = 'logbuch-netzpolitik.de'
        check = PrivacyMissingTwitterCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.NOT_APPLICABLE)
        self.assertEqual(result.passed.passed, True)


class PrivacyMissingMatomoMentionTestCase(BaseMetricCheckTestCase, unittest.TestCase):

    def test_matomo_used_with_mention(self):
        domain = 'berufskleidung24.de'
        check = PrivacyMissingMatomoCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PASSED)

    def test_matomo_used_no_privacy_policy(self):
        domain = 'hohenbogen.de'
        check = PrivacyMissingMatomoCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PRECONDITION_FAILED)

    def test_matomo_not_used(self):
        domain = 'logbuch-netzpolitik.de'
        check = PrivacyMissingMatomoCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.NOT_APPLICABLE)
        self.assertEqual(result.passed.passed, True)


class PrivacyMissingHubspotMentionTestCase(BaseMetricCheckTestCase, unittest.TestCase):

    def test_hubspot_used_no_privacy_policy(self):
        domain = 'goldmarie-friends.de'
        check = PrivacyMissingHubspotCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PRECONDITION_FAILED)


class PrivacyMissingFacebookMentionTestCase(BaseMetricCheckTestCase, unittest.TestCase):

    def test_facebook_used_no_privacy_policy(self):
        domain = 'hohenbogen.de'
        check = PrivacyMissingFacebookPixelCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.PRECONDITION_FAILED)

    def test_facebook_not_used(self):
        domain = 'goldmarie-friends.de'
        check = PrivacyMissingFacebookPixelCheck(domain, self.metadata.get(domain), self.metadata_filepath)
        result = check.check()
        self.assertEqual(result.passed, CheckResult.PassType.NOT_APPLICABLE)


if __name__ == '__main__':
    unittest.main()
