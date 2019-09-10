import logging
from abc import ABC, abstractmethod
from typing import Dict, List

from analyzer.checks.check_result import CheckResult
from analyzer.checks.severity import Severity
from analyzer.types_definitions import CrawlerDomainMetaData

logger = logging.getLogger(__name__)


class MetricCheck(ABC):

    def __init__(self, domain: str, page_types: CrawlerDomainMetaData, meta_data_filepath: str, *args, **kwargs):
        self.domain = domain
        self.page_types = page_types
        self.meta_data_filepath = meta_data_filepath

    def _get_check_result(self, passed: bool) -> CheckResult:
        return CheckResult(domain=self.domain, identifier=self.IDENTIFIER, passed=passed, severity=self.SEVERITY)

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
