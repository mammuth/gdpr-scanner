import logging
from abc import ABC, abstractmethod
from typing import Dict, List

from analyzer import CrawlerDomainMetaData
from analyzer.checks.check_result import CheckResult
from analyzer.checks.severity import Severity

logger = logging.getLogger(__name__)


class MetricCheck(ABC):

    def __init__(self, domain: str, page_types: CrawlerDomainMetaData, meta_data_filepath: str, *args, **kwargs):
        self.domain = domain
        self.page_types = page_types
        self.meta_data_filepath = meta_data_filepath

    @property
    @abstractmethod
    def SEVERITY(self) -> Severity:
        pass

    @abstractmethod
    def check(self) -> CheckResult:
        pass
