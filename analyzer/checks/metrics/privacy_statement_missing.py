import logging

from bs4 import BeautifulSoup

from analyzer.checks.check_result import CheckResult
from analyzer.checks.metrics import MetricCheck
from analyzer.checks.severity import Severity

logger = logging.getLogger(__name__)


class PrivacyStatementMissingCheck(MetricCheck):
    IDENTIFIER = 'privacy-statement-missing'
    SEVERITY = Severity.CRITICAL
    _title_detector_strings = ['Datenschutz', 'Privatsphäre', 'Privacy']

    def check(self) -> CheckResult:
        # logger.debug(f'{self.domain} crawled page_types: {list(self.page_types.items())}')

        privacy_page_type_exists = 'privacy' in self.page_types
        if not privacy_page_type_exists:
            return self._get_check_result(CheckResult.PassType.FAILED)

        # Check whether "Datenschutz" is present in the page body
        for html in self.get_html_strings_of(page_type='privacy'):
            for phrase in self._title_detector_strings:
                res = self.phrase_in_page_title(phrase, html) or self.phrase_in_html_body(phrase, html)
                if res is True:
                    return self._get_check_result(CheckResult.PassType.PASSED)

        return self._get_check_result(CheckResult.PassType.UNCERTAIN)
