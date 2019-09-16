from typing import List

from analyzer.checks.third_party_integrations import ThirdPartyIntegration, ALL_THIRD_PARTY_INTEGRATIONS


def third_parties_in_page(html: str) -> List[ThirdPartyIntegration]:

    found_providers: List[ThirdPartyIntegration] = list()
    for provider in ALL_THIRD_PARTY_INTEGRATIONS:
        for detector in provider.detector_strings:
            if detector in html:
                found_providers.append(provider)
                break
    return found_providers
