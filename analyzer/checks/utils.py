from typing import List

from analyzer.checks.analytics_providers import AnalyticsProvider


def analytics_providers_in_page(html: str) -> List[AnalyticsProvider]:
    found_providers: List[AnalyticsProvider] = list()
    for provider in AnalyticsProvider:
        for detector in provider.detector_strings:
            if detector in html:
                found_providers.append(provider)
                break
    return found_providers
