package crawl

import (
	"fmt"
	"net/url"
	"strings"
	"time"

	"github.com/gocolly/colly"

	"crawler/page"

	"crawler/storage"
	"crawler/utils"
)

// Reports whether the link should be followed or not. Interesting links are: privacy policy, imprint, agbs, contact,
func isPrivacyPolicy(link *colly.HTMLElement) bool {
	interestingWords := []string{"privacy", "datenschutz"}
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

func sanitizeUrlToCrawl(inputUrl string) string {
	if !strings.HasPrefix(inputUrl, "http") {
		return "http://" + inputUrl
	}
	return inputUrl
}

type Crawler struct {
	storage *storage.Storage
}

func (crawler Crawler) RunCrawler(domains []string, threads int) {
	crawlerStorage := storage.Storage{}

	// Instantiate default collector
	c := colly.NewCollector(
		// MaxDepth is 1, so only the links on the scraped page are visited
		colly.MaxDepth(1),
		colly.Async(true),
		colly.IgnoreRobotsTxt(),
		//colly.AllowedDomains(domains...),
	)

	c.SetRequestTimeout(3 * time.Second)

	// Limit the maximum parallelism to eg. 2
	// This is necessary if the goroutines are dynamically
	// created to control the limit of simultaneous requests.
	c.Limit(
		&colly.LimitRule{DomainGlob: "*", Parallelism: threads},
	)

	//c.WithTransport(&http.Transport{
	//	//Proxy: http.ProxyFromEnvironment,
	//	//DialContext: (&net.Dialer{
	//	//	Timeout:   30 * time.Second,
	//	//	KeepAlive: 30 * time.Second,
	//	//	DualStack: true,
	//	//}).DialContext,
	//	//MaxIdleConns:          100,
	//	//DisableKeepAlives: true,
	//	//IdleConnTimeout:       90 * time.Second,
	//	IdleConnTimeout: 3 * time.Second,
	//	//TLSHandshakeTimeout:   10 * time.Second,
	//	//ExpectContinueTimeout: 1 * time.Second,
	//})

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
		pageType := page.TypeFromInterface(r.Ctx.GetAny("pageType"))
		crawlerStorage.StorePageVisit(pageUrl, r.Body, pageType)
	})

	c.OnHTML("a[href]", func(e *colly.HTMLElement) {
		// Check whether we should follow the found href
		if !isExternalLink(e) {
			if isPrivacyPolicy(e) {
				// ToDo: Store url and location to privacy policy. Can we use request context?
				// Visit link found on page on a new thread
				fullUrl, err := utils.LinkToAbsoluteUrl(e)
				if err != nil {
					return
				}
				//e.Request.Visit(sanitizedUrl)  // ToDo: Doesn't seem to work
				//c.Visit(fullUrl)
				ctx := colly.NewContext()
				ctx.Put("pageType", page.PrivacyPage)
				c.Request("GET", fullUrl, nil, ctx, nil)
			}
		}
	})

	c.OnError(func(r *colly.Response, e error) {
		fmt.Println("error visiting", r.Request.URL, e)
	})

	for _, url := range domains {
		ctx := colly.NewContext()
		ctx.Put("pageType", page.IndexPage)
		c.Request("GET", sanitizeUrlToCrawl(url), nil, ctx, nil)
	}

	c.Wait()
	crawlerStorage.NotifyCrawlingFinished()
}

func (crawler Crawler) TearDown() {
	// ToDo: Call this method on on ctrl-C interrupt signal
	crawler.storage.NotifyCrawlingFinished()
}
