import logging
import os
from abc import ABC

from analyzer.checks import MetricCheck, CheckResult, Severity, utils, CheckResultPassed

logger = logging.getLogger(__name__)


class BaseTrackingServiceIPNotAnonymizedCheck(ABC):

    def check(self) -> CheckResult:
        # logger.debug(f'{self.domain} crawled pages: {list(self.page_types)}')
        idx_html_path = self.page_types['index'][0]['htmlFilePath']  # ToDo: Error handling
        idx_html_abspath = os.path.join(os.path.dirname(self.meta_data_filepath), idx_html_path)
        with open(idx_html_abspath, 'rb') as f:
            # don't fail on encoding issues, but replace the faulty characters
            html = f.read().decode('utf-8', errors='replace')
            passed = not self._page_uses_service_without_anonymization(html)
        return self._get_check_result(CheckResultPassed.PASSED if passed else CheckResultPassed.FAILED)


class GoogleAnalyticsIPNotAnonymizedCheck(BaseTrackingServiceIPNotAnonymizedCheck, MetricCheck):
    IDENTIFIER = 'ip-not-anonymized-googleanalytics'
    SEVERITY = Severity.MEDIUM

    def _page_uses_service_without_anonymization(self, html: str) -> bool:
        from analyzer.checks.analytics_providers import AnalyticsProvider
        has_ga = AnalyticsProvider.GOOGLE_ANALYTICS in utils.analytics_providers_in_page(html)
        if has_ga:
            anonymize_detectors = ['anonymize_ip', 'anonymizeIp', ]  # gtag, ga,
            has_anon = False
            for detector in anonymize_detectors:
                if detector in html:
                    has_anon = True
                    break
            return not has_anon
        else:
            return False
