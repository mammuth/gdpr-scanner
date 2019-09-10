import logging

from analyzer.checks import MetricCheck, CheckResult
from analyzer.checks.severity import Severity

logger = logging.getLogger(__name__)


class PrivacyStatementMissingCheck(MetricCheck):
    IDENTIFIER = 'privacy-statement-missing'
    SEVERITY = Severity.CRITICAL

    def check(self) -> CheckResult:
        page_types = self.analyzer.crawler_meta_data.get(self.domain, None)
        logger.debug(f'{self.domain} crawled page_types: {list(page_types.items())}')
        passed = 'privacy' in page_types

        return CheckResult(passed=passed, identifier=self.IDENTIFIER, severity=self.SEVERITY)
