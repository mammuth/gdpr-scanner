package main

import (
	"fmt"
	"net/url"
	"strings"

	"crawler/storage"
	"crawler/utils"

	"github.com/gocolly/colly"
)

// Reports whether the link should be followed or not. Interesting links are: privacy policy, imprint, agbs, contact,
func isInterestingLink(link *colly.HTMLElement) bool {
	interestingWords := []string{"privacy policy", "privacy statement", "privacy", "datenschutz", "datenschutzerklärung"}
	for _, word := range interestingWords {
		if strings.Contains(strings.ToLower(link.Text), word) {
			return true
		}
	}
	return false
}

func isExternalLink(link *colly.HTMLElement) bool {
	hrefUrl, err := url.Parse(link.Attr("href"))
	if err != nil {
		fmt.Println(err)
		return true
	}
	// Relative urls are definitely no external urls
	if !hrefUrl.IsAbs() {
		return false
	}
	return hrefUrl.Host != link.Request.URL.Host
}

func runCrawler() {
	// Instantiate default collector
	c := colly.NewCollector(
		// MaxDepth is 1, so only the links on the scraped page are visited
		colly.MaxDepth(1),
		colly.Async(true),
		colly.IgnoreRobotsTxt(),
	)

	// Limit the maximum parallelism to 2
	// This is necessary if the goroutines are dynamically
	// created to control the limit of simultaneous requests.
	//
	// Parallelism can be controlled also by spawning fixed
	// number of go routines.
	c.Limit(
		&colly.LimitRule{DomainGlob: "*", Parallelism: 2},
	)

	c.OnRequest(func(r *colly.Request) {
		fmt.Println("visiting", r.URL)
	})

	c.OnResponse(func(r *colly.Response) {
		// Store the result
		pageUrl, err := url.Parse(r.Request.URL.String())
		if err != nil {
			println(err)
			return
		}
		storage.StorePageVisit(pageUrl, r.Body)
	})

	c.OnError(func(r *colly.Response, e error) {
		fmt.Println("error visiting", r.Request.URL, e)
	})

	c.OnHTML("a[href]", func(e *colly.HTMLElement) {
		// Check whether we should follow the found href
		if isInterestingLink(e) && !isExternalLink(e) {
			// Visit link found on page on a new thread
			fullUrl, err := utils.LinkToAbsoluteUrl(e)
			if err != nil {
				return
			}
			//e.Request.Visit(sanitizedUrl)  // ToDo: Doesn't seem to work
			c.Visit(fullUrl)
		}
	})

	for _, url := range getUrls() {
		c.Visit(url)
	}

	c.Wait()
}
