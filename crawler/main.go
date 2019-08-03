package main

import (
	"flag"
	"fmt"
	"os"
)

func main() {
	// Command line arguments
	var paramInputUrl string
	flag.StringVar(&paramInputUrl, "url", "", "Single URL to crawl")

	var paramUrlListPath string
	flag.StringVar(&paramUrlListPath, "list", "", "Filepath to url list")

	var paramThreads int
	flag.IntVar(&paramThreads, "threads", 2, "Number of crawler threads")

	flag.Parse()

	if paramInputUrl == "" && paramUrlListPath == "" {
		fmt.Println("Please either specify the url or list parameter")
		os.Exit(2)
	}

	// Get urls to crawl
	var urls []string
	if paramInputUrl != "" {
		urls = []string{paramInputUrl}
	} else {
		urls = loadUrlList(paramUrlListPath)
	}

	runCrawler(urls, paramThreads)
}
