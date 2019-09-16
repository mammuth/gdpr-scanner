from abc import ABC, abstractmethod


class ThirdPartyIntegration(ABC):
    @property
    @abstractmethod
    def identifier(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def detector_strings(self):
        raise NotImplementedError()

    def used_in_page(self, html: str) -> bool:
        """Returns True if the given provider is detected in `html`.
        """
        for detector in self.detector_strings:
            if detector in html:
                return True
        return False


class GoogleAnalytics(ThirdPartyIntegration):
    identifier = 'google-analytics'
    detector_strings = ["ga('send'", "gtag(", "_gaq.push("]


class FacebookTracking(ThirdPartyIntegration):
    identifier = 'facebook-tracking'
    detector_strings = ["fbq(", 'src="https://www.facebook.com/tr?id=', "https://connect.facebook.net"]


class Hubspot(ThirdPartyIntegration):
    identifier = 'hubspot'
    detector_strings = ["js.hs-scripts.com", "js.hs-analytics.net"]


class Twitter(ThirdPartyIntegration):
    identifier = 'twitter'
    detector_strings = ["platform.twitter.com/widgets.js"]


ALL_THIRD_PARTY_INTEGRATIONS = [GoogleAnalytics(), FacebookTracking(), Hubspot(), Twitter()]
