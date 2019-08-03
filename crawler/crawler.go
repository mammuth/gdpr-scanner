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

func runCrawler(urlsToCrawl []string, threads int) {
	// Instantiate default collector
	c := colly.NewCollector(
		// MaxDepth is 1, so only the links on the scraped page are visited
		colly.MaxDepth(1),
		colly.Async(true),
		colly.IgnoreRobotsTxt(),
	)

	// Limit the maximum parallelism to eg. 2
	// This is necessary if the goroutines are dynamically
	// created to control the limit of simultaneous requests.
	c.Limit(
		&colly.LimitRule{DomainGlob: "*", Parallelism: threads},
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

	for _, url := range urlsToCrawl {
		// ToDo: Add http schema to URL in case it's missing
		c.Visit(url)
	}

	c.Wait()
}

//func queueCrawler() {
//	// Instantiate default collector
//	c := colly.NewCollector(
//		colly.AllowURLRevisit(),
//		colly.MaxDepth(1),
//	)
//
//	// create a request queue with 2 consumer threads
//	q, _ := queue.New(
//		2,                                           // Number of consumer threads
//		&queue.InMemoryQueueStorage{MaxSize: 10000}, // Use default queue storage
//	)
//
//	c.OnRequest(func(r *colly.Request) {
//		fmt.Println("visiting", r.URL)
//		//if r.ID < 15 {
//		//	r2, err := r.New("GET", fmt.Sprintf("%s?x=%v", url, r.ID), nil)
//		//	if err == nil {
//		//		q.AddRequest(r2)
//		//	}
//		//}
//	})
//
//	// Identify interesting links
//	c.OnHTML("a[href]", func(e *colly.HTMLElement) {
//		link := e.Attr("href")
//		// Print link
//		fmt.Println(link)
//		// Visit link found on page on a new thread
//		//e.Request.Visit(link)
//		q.AddURL(link)
//	})
//
//	//c.OnResponse(func(r *colly.Response) {
//	//	body := string(r.Body)
//	//	fmt.Print("test")
//	//	fmt.Println("body length of %s %d", r.Request.URL, len(body))
//	//})
//
//	for _, url := range getUrls() {
//		q.AddURL(url)
//	}
//	// Consume URLs
//	q.Run(c)
//}
