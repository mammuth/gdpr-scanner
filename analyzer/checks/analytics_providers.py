from enum import Enum
from typing import List


class AnalyticsProvider(Enum):
    GOOGLE_ANALYTICS = 1
    MATOMO = 2

    @property
    def detector_strings(self) -> List[str]:
        if self is self.GOOGLE_ANALYTICS:
            return ["ga('send'", "gtag(", "_gaq.push("]
        elif self is self.MATOMO:
            return []
