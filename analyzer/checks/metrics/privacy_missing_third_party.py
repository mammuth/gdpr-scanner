import logging
from abc import ABC

from analyzer.checks import utils
from analyzer.checks.check_result import CheckResult
from analyzer.checks.metrics import MetricCheck
from analyzer.checks.severity import Severity
from analyzer.checks.third_party_integrations import GoogleAnalytics, FacebookTracking, Twitter

logger = logging.getLogger(__name__)


class BasePrivacyMissingThirdPartyCheck(ABC):
    SEVERITY = Severity.LOW

    def check(self) -> CheckResult:
        # first determine whether the html of the index page uses the given third party service
        idx_html = self.get_html_strings_of(page_type='index')[0]
        uses_service = self._page_uses_service(idx_html)
        if not uses_service:
            # Index page does not use the given third party service -> no need to mention it in the privacy statement
            return self._get_check_result(CheckResult.PassType.NOT_APPLICABLE)

        if 'privacy' not in self.page_types:
            # Index page uses service but there is no privacy statement -> service not mentioned in privacy statement
            return self._get_check_result(
                CheckResult.PassType.FAILED,
                'The tested third party is used in the index page but there seems to be no privacy statement at all.'
            )

        # It might be that the crawler identified multiple privacy statement pages.
        # We're testing all and return "passed" if one of them passes
        for html in self.get_html_strings_of(page_type='privacy'):
            mention = self._html_mentions_service(html)
            if mention:
                return self._get_check_result(passed=CheckResult.PassType.PASSED)
        return self._get_check_result(passed=CheckResult.PassType.FAILED)


class PrivacyMissingGoogleAnalyticsCheck(BasePrivacyMissingThirdPartyCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-googleanalytics'

    def _page_uses_service(self, html) -> bool:
        return GoogleAnalytics().used_in_page(html)

    def _html_mentions_service(self, html: str) -> bool:
        return any([
            self.phrase_in_html_body('Google Analytics', html),
            self.phrase_in_html_body('Google Tag Manager', html)
        ])


class PrivacyMissingFacebookPixelCheck(BasePrivacyMissingThirdPartyCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-facebook-pixel'

    def _page_uses_service(self, html) -> bool:
        return FacebookTracking().used_in_page(html)

    def _html_mentions_service(self, html: str) -> bool:
        return self.phrase_in_html_body('FacebookTracking Inc', html)


class PrivacyMissingTwitterCheck(BasePrivacyMissingThirdPartyCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-twitter'

    def _page_uses_service(self, html) -> bool:
        return Twitter().used_in_page(html)

    def _html_mentions_service(self, html: str) -> bool:
        return self.phrase_in_html_body('Twitter Inc', html)

# ToDo: Implement more third party integrations:  Matomo (berufsbekleidung) AdSense, Disqus, Instagram, Interecom, ...
