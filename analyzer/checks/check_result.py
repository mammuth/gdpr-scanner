from dataclasses import dataclass
from enum import Enum


@dataclass
class CheckResult:
    class PassType(Enum):
        PASSED = 'passed'
        FAILED = 'failed'
        UNCERTAIN = 'uncertain'
        NOT_APPLICABLE = 'not_applicable'

        def __bool__(self):
            return self is not CheckResult.PassType.FAILED

        @property
        def passed(self):
            """

            :return: True if the test did not fail (== test passed OR test result is uncertain)
            """
            return bool(self)

    domain: str
    identifier: str
    passed: PassType
    description: str
    severity: 'Severity'

    def __str__(self):
        return f'{self.domain} - {self.identifier}: {self.passed}'
