package main

// ToDo: Proper Logging
// ToDo: Improve error handling

import (
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"strings"

	"crawler/crawl"
)

func main() {
	// Command line arguments
	var paramInputDomain string
	flag.StringVar(&paramInputDomain, "domain", "", "Single domain to crawl")

	var paramDomainList string
	flag.StringVar(&paramDomainList, "list", "", "Filepath to domain list. Should contain one domain (without schema) per line")

	var paramThreads int
	flag.IntVar(&paramThreads, "threads", 2, "Number of crawl threads")

	flag.Parse()

	if paramInputDomain == "" && paramDomainList == "" {
		fmt.Println("Please either specify the url or list parameter")
		os.Exit(2)
	}

	// Get urls to crawl
	var urls []string
	if paramInputDomain != "" {
		urls = []string{paramInputDomain}
	} else {
		content, err := ioutil.ReadFile(paramDomainList)
		if err != nil {
			fmt.Println(err)
			os.Exit(2)
		}
		urls = strings.Split(string(content), "\n")
	}

	crawler := crawl.Crawler{}
	crawler.RunCrawler(urls, paramThreads)
}
