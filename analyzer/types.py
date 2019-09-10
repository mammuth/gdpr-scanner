from typing import Dict, List

CrawlerDomainMetaData = Dict[str, List]  # pageType->crawledPages
CrawlerMetaData = Dict[str, CrawlerDomainMetaData]  # CrawlerDomainMetaData
