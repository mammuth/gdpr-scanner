# GDPR Scanner

The gdpr scanner consists of multiple components

1. A web crawler, located at `crawler/`, written in Go
2. An analyzing service, located at `analyzer/`, written in Python

## Usage

#### Crawler

The crawler can be built using the `build.sh` script. Binaries for linux, macOS and Windows will be stored at `dist/.

**Parameter options**:
- `-domain <domain>` or `-list <path>` is used for specifying the domains to crawl
- Optional: `-threads`  specifies the number of parallel threads
- Optional: `-verbose` for verbose/debugging log output. Not recommended for large lists

**Examples**:
- `./crawler -domain www.maxi-muth.de -threads 20 -verbose`
- `./crawler -list domain-list.txt` (The list should contain line-separated domains, not full URLs).

The results will be stored in the directory `output/`. It contains a meta data file `crawler.json` which tracks which domains got crawled with which pages and an estimation of the type of page (eg. privacy policy or contact page).


#### Analyzer

The analyzer CLI can be run with python 3.7:
- `python main.py analyze` 

Available options can be printed using `--help` or by just calling `main.py` without the `analyze` command. 