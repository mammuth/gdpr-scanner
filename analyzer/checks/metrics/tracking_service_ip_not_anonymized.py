import logging
import os
from abc import ABC, abstractmethod

from analyzer.checks import detectors
from analyzer.checks.check_result import CheckResult
from analyzer.checks.metrics import MetricCheck
from analyzer.checks.severity import Severity

logger = logging.getLogger(__name__)


class BaseTrackingServiceIPNotAnonymizedCheck(ABC):

    def check(self) -> CheckResult:
        # logger.debug(f'{self.domain} crawled pages: {list(self.page_types)}')
        idx_html_path = self.page_types['index'][0]['htmlFilePath']  # ToDo: Error handling
        idx_html_abspath = os.path.join(os.path.dirname(self.meta_data_filepath), idx_html_path)
        with open(idx_html_abspath, 'rb') as f:
            # don't fail on encoding issues, but replace the faulty characters
            html = f.read().decode('utf-8', errors='replace')
            result: CheckResult.PassType
            if self._page_uses_service(html):
                result = CheckResult.PassType.FAILED if self._service_anonymization_not_implemented(html) \
                    else CheckResult.PassType.PASSED
            else:
                result = CheckResult.PassType.NOT_APPLICABLE
        return self._get_check_result(result)

    @abstractmethod
    def _page_uses_service(self, html):
        raise NotImplementedError()

    @abstractmethod
    def _service_anonymization_not_implemented(self, html):
        raise NotImplementedError()


class GoogleAnalyticsIPNotAnonymizedCheck(BaseTrackingServiceIPNotAnonymizedCheck, MetricCheck):
    IDENTIFIER = 'ip-not-anonymized-googleanalytics'
    SEVERITY = Severity.MEDIUM

    def _page_uses_service(self, html: str) -> bool:
        return detectors.page_uses_service(html, detectors.GOOGLE_ANALYTICS)

    def _service_anonymization_not_implemented(self, html):
        anonymize_detectors = ['anonymize_ip', 'anonymizeIp', ]  # gtag, ga,
        has_anon = False
        for detector in anonymize_detectors:
            if detector in html:
                has_anon = True
                break
        return not has_anon

ALL_METRICS = [
    GoogleAnalyticsIPNotAnonymizedCheck,
]