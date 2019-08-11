package main

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

	var paramVerbose bool
	flag.BoolVar(&paramVerbose, "verbose", false, "Enable verbose log output")

	flag.Parse()

	if paramInputDomain == "" && paramDomainList == "" {
		fmt.Println("Please either specify the url or list parameter")
		os.Exit(2)
	}

	// Get domains to crawl
	var domains []string
	if paramInputDomain != "" {
		domains = []string{paramInputDomain}
	} else {
		content, err := ioutil.ReadFile(paramDomainList)
		if err != nil {
			fmt.Println(err)
			os.Exit(2)
		}
		domains = strings.Split(string(content), "\n")
	}

	crawler := crawl.New(domains, paramThreads, paramVerbose)
	crawler.Run()
}
