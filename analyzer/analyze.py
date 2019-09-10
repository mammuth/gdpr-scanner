import json
import logging
import os
from collections import defaultdict
from typing import List, Dict, Optional

from analyzer import CrawlerMetaData
from analyzer.checks import MetricCheck, CheckResult
from analyzer.checks.privacy_statement_missing import PrivacyStatementMissingCheck
from analyzer.checks.tracking_service_ip_not_anonymized import TrackingServiceIPNotAnonymizedCheck
from analyzer.exceptions import InvalidMetricCheckException

logger = logging.getLogger(__name__)


class Analyzer:
    checks: List[MetricCheck] = [PrivacyStatementMissingCheck, TrackingServiceIPNotAnonymizedCheck, ]

    def __init__(self, crawler_metadata_filepath: str, checks: List[MetricCheck] = None, *args, **kwargs):
        self.crawler_metadata_filepath = crawler_metadata_filepath
        self.crawler_meta_data = self._import_crawler_meta(path=os.path.abspath(crawler_metadata_filepath))
        if checks:
            self.checks = checks

    def _import_crawler_meta(self, path: str) -> Optional[CrawlerMetaData]:
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
        return None

    def run(self, specific_domain: str = None):
        if specific_domain is True:
            page_types = self.crawler_meta_data.get(specific_domain)
            self._checks_for_domain(specific_domain, page_types)
        else:
            for domain, page_types in self.crawler_meta_data.items():
                self._checks_for_domain(domain, page_types)

    def _checks_for_domain(self, domain: str, page_types):
        for check_class in self.checks:
            check = check_class(domain, page_types, self.crawler_metadata_filepath)  # noqa
            if not isinstance(check, MetricCheck):
                raise InvalidMetricCheckException()
            result: CheckResult = check.check()
            logger.info(f'{domain} {result.identifier} {result.passed}')
