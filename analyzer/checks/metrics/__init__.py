import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Dict, List

from bs4 import BeautifulSoup

from analyzer.checks.check_result import CheckResult
from analyzer.checks.severity import Severity
from analyzer.types_definitions import CrawlerDomainMetaData

logger = logging.getLogger(__name__)


class MetricCheck(ABC):

    def __init__(self, domain: str, page_types: CrawlerDomainMetaData, meta_data_filepath: str, *args, **kwargs):
        self.domain = domain
        self.page_types = page_types
        self.meta_data_filepath = meta_data_filepath

    def _get_check_result(self, passed: CheckResult.PassType, description: str = '') -> CheckResult:
        return CheckResult(
            domain=self.domain,
            identifier=self.IDENTIFIER,
            passed=passed,
            severity=self.SEVERITY,
            description=description
        )

    def get_html_strings_of(self, page_type: str) -> List[str]:
        html_strings: List[str] = list()
        for page in self.page_types.get(page_type, []):
            html_abspath = os.path.join(os.path.dirname(self.meta_data_filepath), page['htmlFilePath'])
            with open(html_abspath, 'rb') as f:
                # don't fail on encoding issues, but replace the faulty characters
                html = f.read().decode('utf-8', errors='replace')
                html_strings.append(html)
        return html_strings

    def phrase_in_html_body(self, phrase: str, html: str) -> bool:
        # ToDo: Don't instantiate bs for every call, share it across checks based on the html content / hash
        soup = BeautifulSoup(html, 'html.parser')
        # We're compiling a regex here, otherwise bs4 would only return for *exact* matches.
        return soup.find(text=re.compile(phrase, re.IGNORECASE)) is not None

    def phrase_in_page_title(selfself, phrase: str, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')
        # We're compiling a regex here, otherwise bs4 would only return for *exact* matches.
        return soup.find('title', text=re.compile(phrase, re.IGNORECASE)) is not None

    @property
    @abstractmethod
    def SEVERITY(self) -> Severity:
        pass

    @property
    @abstractmethod
    def IDENTIFIER(self) -> str:
        pass

    @abstractmethod
    def check(self) -> CheckResult:
        pass
