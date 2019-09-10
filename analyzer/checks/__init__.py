import logging
from abc import ABC, abstractmethod

from analyzer.checks.check_result import CheckResult
from analyzer.checks.severity import Severity

logger = logging.getLogger(__name__)


class MetricCheck(ABC):

    # ToDo: Only pass metadata and metadata filepath (to resolve the relative html paths)?
    def __init__(self, analyzer: 'Analyzer', domain: str, *args, **kwargs):
        self.analyzer = analyzer
        self.domain = domain

    @property
    @abstractmethod
    def SEVERITY(self) -> Severity:
        pass

    @abstractmethod
    def check(self) -> CheckResult:
        pass
