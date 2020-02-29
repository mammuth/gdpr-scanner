# GDPR Scanner

The gdpr scanner is a tool which checks a list of domains for violations against the GDPR. It implements a test-suite with pre-defined test cases and also makes it easy to add your own tests.


It consists of two components

1. A web crawler, located at `crawler/`, written in Go
2. An analyzing service, located at `analyzer/`, written in Python

## Example test cases
- `privacy-statement-missing`: Checks whether the given side has a privacy policy.
- `ip-not-anonymized-[tracking-provider]`: Checks whether tracking services like Google Analytics have IP anonymization enabled.
- `privacy-missing-thirdparty-[thirdparty]`: Checks whether third party tools are used in the page and whether they're mentioned in the privacy statement if they're known to handle personal data.
- `privacy-missing-[paragraph]`: Checks whether the privacy statement misses a mention of something which is needed.

## Crawler

The crawler can be built using the `build.sh` script. Binaries for linux, macOS and Windows will be stored at `dist/`.

**Parameter options**:
- `-domain <domain>` or `-list <path>` is used for specifying the domains to crawl
- Optional: `-threads`  specifies the number of parallel threads
- Optional: `-verbose` for verbose/debugging log output. Not recommended for large lists

**Examples**:
- `./crawler -domain www.maxi-muth.de -threads 20 -verbose`
- `./crawler -list domain-list.txt` (The list should contain line-separated domains, not full URLs).
- Log to file: `./crawler -list lists/list_test_1k.txt -threads 20 > crawler_1k.log 2>&1 &`

The results will be stored in the directory `output/`. It contains a meta data file `crawler.json` which tracks which domains got crawled with which pages and an estimation of the type of page (eg. privacy policy or contact page).


## Analyzer

The analyzer CLI can be run with python 3.7 from the root of the repository:
- `python -m analyzer analyze` 

Available options can be printed using `--help` or by just calling `analyzer` without the `analyze` command. 

Note that some few dependencies are required; you can install them by running `pipenv install` in the `analyzer` directory.

Tests can be run with `python -m unittest discover`

**Troubleshooting**
If you get a `ModuleNotFoundError` when running the unpackaged python app, add the directory to your python path (execute at the root of the repository): 
`export PYTHONPATH="${PYTHONPATH}:$(pwd)"`
