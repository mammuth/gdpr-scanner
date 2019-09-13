import logging

from analyzer.checks.check_result import CheckResult
from analyzer.checks.metrics import MetricCheck
from analyzer.checks.severity import Severity

logger = logging.getLogger(__name__)


class PrivacyStatementMissingCheck(MetricCheck):
    IDENTIFIER = 'privacy-statement-missing'
    SEVERITY = Severity.CRITICAL

    def check(self) -> CheckResult:
        # logger.debug(f'{self.domain} crawled page_types: {list(self.page_types.items())}')
        passed = 'privacy' in self.page_types
        return self._get_check_result(CheckResult.PassType.PASSED if passed else CheckResult.PassType.FAILED)
