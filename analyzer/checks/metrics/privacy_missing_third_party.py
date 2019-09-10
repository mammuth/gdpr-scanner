import logging
from abc import ABC

from analyzer.checks import CheckResult, Severity, utils, MetricCheck

logger = logging.getLogger(__name__)


class BasePrivacyMissingThirdPartyCheck(ABC):
    SEVERITY = Severity.LOW

    def check(self) -> CheckResult:
        # first determine whether the html of the index page uses the given third party service
        idx_html = self.get_html_strings_of(page_type='index')[0]
        uses_service = self._page_uses_service(idx_html)
        if not uses_service:
            # Index page does not use the given third party service -> no need to mention it in the privacy statement
            # ToDo: should be not True, but rather uncertain / not tested? Maybe return Optional[CheckResult]?
            return self._get_check_result(True)

        if 'privacy' not in self.page_types:
            # Index page uses service but there is no privacy statement -> service not mentioned in privacy statement
            return self._get_check_result(False)

        # It might be that the crawler identified multiple privacy statement pages.
        # We're testing all and return "passed" if one of them passes
        for html in self.get_html_strings_of(page_type='privacy'):
            mention = self._html_mentions_service(html)
            if mention:
                return self._get_check_result(passed=True)
        return self._get_check_result(passed=False)


class PrivacyMissingGoogleAnalyticsCheck(BasePrivacyMissingThirdPartyCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-googleanalytics'

    def _page_uses_service(self, html) -> bool:
        from analyzer.checks.analytics_providers import AnalyticsProvider
        has_ga = AnalyticsProvider.GOOGLE_ANALYTICS in utils.analytics_providers_in_page(html)
        return has_ga

    def _html_mentions_service(self, html: str) -> bool:
        return 'Google Analytics' in html  # ToDo: Properly examine body / container instead of whole DOM

# ToDo: Implement more third party integrations: Disqus, Hubspot, Facebook, Instagram, Interecom, ...
