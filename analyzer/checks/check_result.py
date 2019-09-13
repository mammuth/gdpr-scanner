from dataclasses import dataclass
from enum import Enum


class CheckResultPassed(Enum):
    PASSED = 1
    FAILED = 2
    UNCERTAIN = 3

    def __bool__(self):
        return self in [CheckResultPassed.PASSED, CheckResultPassed.UNCERTAIN]

    @property
    def passed(self):
        """

        :return: True if the test did not fail (== test passed OR test result is uncertain)
        """
        return bool(self)


@dataclass
class CheckResult:
    domain: str
    identifier: str
    passed: CheckResultPassed
    severity: 'Severity'
