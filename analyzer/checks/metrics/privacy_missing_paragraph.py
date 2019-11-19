import logging
from abc import abstractmethod
from typing import List

from bs4 import BeautifulSoup

from analyzer.checks.check_result import CheckResult
from analyzer.checks.metrics import MetricCheck
from analyzer.checks.severity import Severity

logger = logging.getLogger(__name__)


class BasePrivacyMissingParagraphCheck(MetricCheck):
    def check(self) -> CheckResult:
        if 'privacy' not in self.page_types:
            return self._get_check_result(
                CheckResult.PassType.PRECONDITION_FAILED, 'There seems to be no privacy statement at all.'
            )

        # It might be that the crawler identified multiple privacy statement pages.
        # We're testing all and return "passed" if one of them passes
        for html in self.get_html_strings_of(page_type='privacy'):
            mention = self._html_mentions_phrase(html)
            if mention:
                return self._get_check_result(passed=CheckResult.PassType.PASSED)
        logger.debug(f'{self.domain} {self.IDENTIFIER} failed')
        return self._get_check_result(passed=CheckResult.PassType.FAILED)

    def _html_mentions_phrase(self, html: str) -> bool:
        """Returns True if the given provider is mentioned in `html`.
        """
        for detector in self._detector_strings:
            match = self.phrase_in_html_body(detector, html)
            if match:
                return True
        return False

    @property
    @abstractmethod
    def _detector_strings(self) -> List[str]:
        raise NotImplementedError


class GDPRInformationRequestMissingCheck(BasePrivacyMissingParagraphCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-information-request'
    SEVERITY = Severity.LOW
    _detector_strings = ['Auskunft', 'Art. 15', 'Artikel 15', 'Auskunftserteilung',]


class GDPRInformationDeletionMissingCheck(BasePrivacyMissingParagraphCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-information-deletion-request'
    SEVERITY = Severity.MEDIUM
    _detector_strings = ['Löschung', 'Recht auf Vergessen', 'Art. 17', 'Artikel 17', 'Art. 18', 'Artikel 18']


class GDPRRevocationMissingCheck(BasePrivacyMissingParagraphCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-revocation'
    SEVERITY = Severity.MEDIUM
    _detector_strings = ['Widerruf', 'Art. 7', 'Artikel 7', 'Widerrufsrecht', 'Recht auf Widerruf', ]


class GDPRObjectMissingCheck(BasePrivacyMissingParagraphCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-object'
    SEVERITY = Severity.MEDIUM
    _detector_strings = ['Widerspruch', 'Recht auf Widerspruch', 'Widerspruchsrecht', 'Art. 21', 'Artikel 21']


class GDPRComplaintMissingCheck(BasePrivacyMissingParagraphCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-complaint'
    SEVERITY = Severity.LOW
    _detector_strings = ['Beschwerde', 'beschweren', 'Art. 77', 'Artikel 77', 'Recht auf Beschwerde', 'Beschwerde bei einer Aufsichtsbehörde', 'Beschwerderecht']


class GDPRPortabilityMissingCheck(BasePrivacyMissingParagraphCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-portability'
    SEVERITY = Severity.LOW
    _detector_strings = ['Datenübertragbarkeit', 'Recht auf Datenübertragung', 'Art. 20', 'Artikel 20']


class GDPRNonEuTransmissionMissingCheck(BasePrivacyMissingParagraphCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-non-eu-transmission'
    SEVERITY = Severity.LOW
    _detector_strings = ['Drittstaat', 'Drittland',  'Mitgliedstaat', 'Datenübermittlung in Drittstaaten', 'Datenübertragung in Drittstaaten', 'Art. 44', 'Artikel 44']

    def check(self) -> CheckResult:
        if 'privacy' not in self.page_types:
            return self._get_check_result(
                CheckResult.PassType.PRECONDITION_FAILED, 'There seems to be no privacy statement at all.'
            )

        # It might be that the crawler identified multiple privacy statement pages.
        # We're testing all and return "passed" if one of them passes
        for html in self.get_html_strings_of(page_type='privacy'):
            mention = self._html_mentions_phrase(html)
            if mention:
                return self._get_check_result(passed=CheckResult.PassType.PASSED)
        logger.debug(f'{self.domain} {self.IDENTIFIER} uncertain')
        return self._get_check_result(passed=CheckResult.PassType.UNCERTAIN, description='Uncertain because we cannot tell whether transmissions occured')


class GDPRRectificationMissingCheck(BasePrivacyMissingParagraphCheck, MetricCheck):
    IDENTIFIER = 'privacy-missing-rectification'
    SEVERITY = Severity.LOW
    _detector_strings = ['Richtigstellung', 'Korrektur', 'Berichtigung', 'Art. 16', 'Artikel 16']


class ProtectionOfficerMissingContactDetailsCheck(MetricCheck):
    IDENTIFIER = 'privacy-missing-officer-contact-details'
    SEVERITY = Severity.MEDIUM

    _email__detector_strings = ['E-Mail', 'Email', 'Mail', '@']
    _phone__detector_strings = ['Telefon', 'Mobil']
    _officer__detector_strings = ['Datenschutzbeauftragter', 'verantwortliche Datenschutzbeauftragte', 'Datenschutzbeauftragten']

    def check(self) -> CheckResult:
        if 'privacy' not in self.page_types:
            return self._get_check_result(
                CheckResult.PassType.PRECONDITION_FAILED, 'There seems to be no privacy statement at all.'
            )

        found_officer = False
        for html in self.get_html_strings_of(page_type='privacy'):
            soup = BeautifulSoup(html, 'html.parser')
            if soup.body is None:
                continue

            # Check whether there is a section about the data protection officer
            txt: str = soup.body.text
            for detector in self._officer__detector_strings:
                position_data_protection_officer = txt.find(detector)
                if position_data_protection_officer != -1:
                    # There is an officer -> Check whether we find an email or phone number within the next lines
                    found_officer = True
                    lookup_text_range = txt[position_data_protection_officer-200:position_data_protection_officer+1500]
                    for s in self._email__detector_strings + self._phone__detector_strings:
                        found = lookup_text_range.find(s)
                        if found != -1:
                            return self._get_check_result(
                                CheckResult.PassType.PASSED, 'The stated data protection officer has contact details'
                            )
        # If we get here, we didn't find a candidate at all or only candidates without contact details
        if found_officer is True:
            # We found an officer without contact details
            logger.debug(f'{self.domain} {self.IDENTIFIER} failed')
            return self._get_check_result(
                CheckResult.PassType.FAILED, 'The stated data protection officer has no contact details'
            )
        else:
            return self._get_check_result(
                CheckResult.PassType.UNCERTAIN, 'No protection officer was mentioned at all'
            )


ALL_METRICS = [
    GDPRInformationRequestMissingCheck,
    GDPRInformationDeletionMissingCheck,
    GDPRRevocationMissingCheck,
    GDPRObjectMissingCheck,
    GDPRComplaintMissingCheck,
    GDPRPortabilityMissingCheck,
    GDPRNonEuTransmissionMissingCheck,
    GDPRRectificationMissingCheck,
    ProtectionOfficerMissingContactDetailsCheck,
]
