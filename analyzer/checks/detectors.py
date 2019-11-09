from typing import List


def page_uses_service(html: str, detector_strings: List[str]) -> bool:
    """Returns True if the given provider is detected in `html`.
    """
    for detector in detector_strings:
        if detector in html:
            return True
    return False


GOOGLE_ANALYTICS = ["ga('send'", 'ga("send"', "gtag(", "_gaq.push("]
MATOMO = ['piwik.php', 'piwik.js']
HUBSPOT = ["js.hs-scripts.com", "js.hs-analytics.net"]

TWITTER = ["platform.twitter.com/widgets.js"]
FACEBOOK = ["fbq(", 'src="https://www.facebook.com/tr?id=', "https://connect.facebook.net"]
