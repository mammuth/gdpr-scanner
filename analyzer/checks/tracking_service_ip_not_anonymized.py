import logging
import os

from analyzer.checks import MetricCheck, CheckResult, Severity

logger = logging.getLogger(__name__)


class TrackingServiceIPNotAnonymized(MetricCheck):
    IDENTIFIER = 'ip-not-anonymized-googleanalytics'  # ToDo: Other tracking providers ip-not-anonymized-[tracking-provider]
    SEVERITY = Severity.CRITICAL

    def check(self) -> CheckResult:
        page_types = self.analyzer.crawler_meta_data.get(self.domain, None)
        logger.debug(f'{self.domain} crawled pages: {list(page_types)}')
        idx_html_path = page_types['index'][0]['htmlFilePath']  # ToDo: Error handling
        idx_html_abspath = os.path.join(os.path.dirname(self.analyzer.crawler_metadata_filepath), idx_html_path)
        with open(idx_html_abspath, 'r', encoding='utf-8') as f:
            html = f.read()
            passed = "ga('send', 'pageview');" not in html or "ga('set', 'anonymizeIp', true);" in html
        return CheckResult(passed=passed, identifier=self.IDENTIFIER, severity=self.SEVERITY)
