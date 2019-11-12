import logging
from abc import ABC, abstractmethod
from typing import List

from analyzer.checks import detectors
from analyzer.checks.check_result import CheckResult
from analyzer.checks.metrics import MetricCheck
from analyzer.checks.severity import Severity

logger = logging.getLogger(__name__)


class BasePrivacyMissingThirdPartyCheck(ABC):
    SEVERITY = Severity.LOW

    def check(self) -> CheckResult:
        # first determine whether the html of the index page uses the given third party service
        idx_html = self.get_html_strings_of(page_type='index')[0]
        uses_service = detectors.page_uses_service(idx_html, self._detector_strings)
        if not uses_service:
            # Index page does not use the given third party service -> no need to mention it in the privacy statement
            return self._get_check_result(CheckResult.PassType.NOT_APPLICABLE)

        if 'privacy' not in self.page_types:
            # Index page uses service but there is no privacy statement -> service not mentioned in privacy statement
            logger.debug(f'{self.domain} {self.IDENTIFIER} is used without having a privacy policy!')
            return self._get_check_result(
                CheckResult.PassType.PRECONDITION_FAILED,
                'The tested third party is used in the index page but there seems to be no privacy statement at all.'
            )

        # It might be that the crawler identified multiple privacy statement pages.
        # We're testing all and return "passed" if one of them passes
        for html in self.get_html_strings_of(page_type='privacy'):
            mention = self.html_mentions_service(html)
            if mention:
                logger.debug(f'{self.domain} passed!')
                return self._get_check_result(passed=CheckResult.PassType.PASSED)
        logger.debug(f'{self.domain} {self.IDENTIFIER} failed')
        return self._get_check_result(passed=CheckResult.PassType.FAILED)

    def html_mentions_service(self, html: str) -> bool:
        """Returns True if the given provider is mentioned in `html`.
        """
        for detector in self._mention_detector_strings:
            match = self.phrase_in_html_body(detector, html)
            if match:
                return True
        return False

    @property
    @abstractmethod
    def _detector_strings(self) -> List[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def _mention_detector_strings(self) -> str:
        raise NotImplementedError


class PrivacyMissingGoogleAnalyticsCheck(BasePrivacyMissingThirdPartyCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-thirdparty-googleanalytics'
    _detector_strings = detectors.GOOGLE_ANALYTICS
    _mention_detector_strings = ['Google Analytics', 'Google Tag Manager']


class PrivacyMissingFacebookPixelCheck(BasePrivacyMissingThirdPartyCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-thirdparty-facebook-pixel'
    _detector_strings = detectors.FACEBOOK
    _mention_detector_strings = ['Facebook Inc']


class PrivacyMissingTwitterCheck(BasePrivacyMissingThirdPartyCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-thirdparty-twitter'
    _detector_strings = detectors.TWITTER
    _mention_detector_strings = ['Twitter Inc']


class PrivacyMissingMatomoCheck(BasePrivacyMissingThirdPartyCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-thirdparty-matomo'
    _detector_strings = detectors.MATOMO
    _mention_detector_strings = ['Piwik', 'Matomo']


class PrivacyMissingHubspotCheck(BasePrivacyMissingThirdPartyCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-thirdparty-hubspot'
    _detector_strings = detectors.HUBSPOT
    _mention_detector_strings = ['Hubspot Inc']


# ToDo: Implement more third party integrations: AdSense, Disqus, Instagram, Interecom, ...
ALL_METRICS = [
    PrivacyMissingGoogleAnalyticsCheck,
    PrivacyMissingMatomoCheck,
    PrivacyMissingFacebookPixelCheck,
    PrivacyMissingTwitterCheck,
    PrivacyMissingHubspotCheck,
]