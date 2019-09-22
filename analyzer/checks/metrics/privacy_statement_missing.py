import logging

from bs4 import BeautifulSoup

from analyzer.checks.check_result import CheckResult
from analyzer.checks.metrics import MetricCheck
from analyzer.checks.severity import Severity

logger = logging.getLogger(__name__)


class PrivacyStatementMissingCheck(MetricCheck):
    IDENTIFIER = 'privacy-statement-missing'
    SEVERITY = Severity.CRITICAL

    def check(self) -> CheckResult:
        # logger.debug(f'{self.domain} crawled page_types: {list(self.page_types.items())}')
        privacy_page_type_exists = 'privacy' in self.page_types
        if not privacy_page_type_exists:
            return self._get_check_result(CheckResult.PassType.FAILED)

        # Check whether "Datenschutz" is present in the bodys text
        passed = False
        for html in self.get_html_strings_of(page_type='privacy'):
            res = self.phrase_in_page_title('Datenschutz', html)
            if res is True:
                passed = True
                break

        return self._get_check_result(CheckResult.PassType.PASSED if passed else CheckResult.PassType.FAILED)
