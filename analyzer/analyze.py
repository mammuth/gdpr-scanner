import json
import logging
import os
from collections import defaultdict
from typing import List, Dict, Optional

from analyzer.checks import MetricCheck, CheckResult
from analyzer.checks.privacy_statement_missing import PrivacyStatementMissingCheck
from analyzer.checks.tracking_service_ip_not_anonymized import TrackingServiceIPNotAnonymized
from analyzer.exceptions import InvalidMetricCheckException

logger = logging.getLogger(__name__)


class Analyzer:
    checks: List[MetricCheck] = [PrivacyStatementMissingCheck, TrackingServiceIPNotAnonymized, ]

    def __init__(self, crawler_metadata_filepath: str, checks: List[MetricCheck] = None, *args, **kwargs):
        self.crawler_metadata_filepath = crawler_metadata_filepath
        self.crawler_meta_data = self._import_crawler_meta(path=os.path.abspath(crawler_metadata_filepath))
        if checks:
            self.checks = checks

    def _import_crawler_meta(self, path: str):
        """

        :param path:
        :param overwrite:
        :return: Dict[OriginalDomain]->Dict[pageType]->List[crawledPageDictionary]
        """
        with open(path) as meta_file:
            raw_json = json.loads(meta_file.read())
            grouped_by_domain = defaultdict(lambda: defaultdict(list))
            for page in raw_json.get('crawledPages'):
                grouped_by_domain[page.get('originalDomain', None)][page.get('pageType', None)].append(page)
            return grouped_by_domain
        return None


    def run(self):
        # ToDo: domain for loop
        domain = 'lupus-ddns.de'

        for check_class in self.checks:
            check = check_class(analyzer=self, domain=domain)  # noqa
            if not isinstance(check, MetricCheck):
                raise InvalidMetricCheckException()
            result: CheckResult = check.check()
            logger.info(f'{domain} {result.identifier} {result.passed}')
