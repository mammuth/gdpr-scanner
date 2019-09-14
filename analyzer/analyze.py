import json
import logging
import os
import time
from collections import defaultdict
from typing import List

from analyzer.checks.check_result import CheckResult
from analyzer.checks.metrics import MetricCheck
from analyzer.checks.metrics.privacy_missing_third_party import PrivacyMissingGoogleAnalyticsCheck
from analyzer.checks.metrics.privacy_statement_missing import PrivacyStatementMissingCheck
from analyzer.checks.metrics.tracking_service_ip_not_anonymized import GoogleAnalyticsIPNotAnonymizedCheck
from analyzer.exceptions import InvalidMetricCheckException, ToDo
from analyzer.types_definitions import CrawlerMetaData

logger = logging.getLogger(__name__)


class Analyzer:
    checks: List[MetricCheck] = [
        PrivacyStatementMissingCheck,
        GoogleAnalyticsIPNotAnonymizedCheck,
        PrivacyMissingGoogleAnalyticsCheck,
    ]

    def __init__(self, crawler_metadata_filepath: str, checks: List[MetricCheck] = None, *args, **kwargs):
        self.crawler_metadata_filepath = crawler_metadata_filepath
        self.crawler_meta_data = self._import_crawler_meta(path=os.path.abspath(crawler_metadata_filepath))
        self.results: List[CheckResult] = list()
        if checks:
            self.checks = checks

    def _import_crawler_meta(self, path: str) -> CrawlerMetaData:
        """

        :param path:
        :param overwrite:
        :return:
        """
        with open(path) as meta_file:
            raw_json = json.loads(meta_file.read())
            grouped_by_domain = defaultdict(lambda: defaultdict(list))
            for page in raw_json.get('crawledPages'):
                grouped_by_domain[page.get('originalDomain', None)][page.get('pageType', None)].append(page)
            return grouped_by_domain

    def failed_checks(self, identifier=None) -> List[CheckResult]:
        if identifier:
            return [
                r for r in self.results
                if r.identifier == identifier and r.passed is CheckResult.PassType.FAILED
            ]
        else:
            return [
                r for r in self.results
                if r.passed is CheckResult.PassType.FAILED
            ]

    def run(self, specific_domain: str = None):
        start_time = time.time()
        if specific_domain is True:
            page_types = self.crawler_meta_data.get(specific_domain)
            self._checks_for_domain(specific_domain, page_types)
        else:
            logger.info(f'Scan started')
            logger.info(f'Number of pages: {len(self.crawler_meta_data)}')
            logger.info(f'Activated checks: {", ".join([check.IDENTIFIER for check in self.checks])}')
            for domain, page_types in self.crawler_meta_data.items():
                self._checks_for_domain(domain, page_types)
        logger.info(f'Scan finished after {round(time.time() - start_time, 2)} seconds')

        # Print statistics
        for check in self.checks:
            failed = self.failed_checks(identifier=check.IDENTIFIER)
            logger.info(f'{check.IDENTIFIER} failed on {len(failed)} pages')

    def write_results_to_file(self):
        raise ToDo()

    def _checks_for_domain(self, domain: str, page_types):
        for check_class in self.checks:
            check = check_class(domain, page_types, self.crawler_metadata_filepath)  # noqa
            if not isinstance(check, MetricCheck):
                raise InvalidMetricCheckException(f'{check.__class__} is no valid MetricCheck')
            try:
                result: CheckResult = check.check()
                self.results.append(result)
            except Exception as e:
                logger.error(f'{domain} {check.IDENTIFIER} CHECK FAILED', exc_info=True)
            else:
                if result.passed is False:
                    logger.debug(f'{domain} {result.identifier} {result.passed}', extra={'domain': domain, 'check': check.IDENTIFIER})
