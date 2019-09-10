import logging
import os

from analyzer.checks import MetricCheck, CheckResult, Severity

logger = logging.getLogger(__name__)


class TrackingServiceIPNotAnonymizedCheck(MetricCheck):
    IDENTIFIER = 'ip-not-anonymized-googleanalytics'  # ToDo: Other tracking providers ip-not-anonymized-[tracking-provider]
    SEVERITY = Severity.MEDIUM

    # ToDo: optimize / complete
    def _page_has_non_anonymized_google_analytics(self, html: str) -> bool:
        analytics_detectors = ["ga('send'", "gtag(", "_gaq.push("]
        has_ga = False
        for detector in analytics_detectors:
            if detector in html:
                has_ga = True
                break
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

    def check(self) -> CheckResult:
        logger.debug(f'{self.domain} crawled pages: {list(self.page_types)}')
        idx_html_path = self.page_types['index'][0]['htmlFilePath']  # ToDo: Error handling
        idx_html_abspath = os.path.join(os.path.dirname(self.meta_data_filepath), idx_html_path)
        with open(idx_html_abspath, 'rb') as f:
            # don't fail on encoding issues, but replace the faulty characters
            html = f.read().decode('utf-8', errors='replace')
            passed = not self._page_has_non_anonymized_google_analytics(html)
        return self._get_check_result(passed)
