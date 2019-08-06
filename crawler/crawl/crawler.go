package crawl

import (
	"fmt"
	"net/url"
	"time"

	"github.com/gocolly/colly"

	"crawler/page"

	"crawler/storage"
	"crawler/utils"
)

type Crawler struct {
	Domains      []string
	CrawlThreads int
	Storage      *storage.Storage
}

func New(domains []string, crawlThreads int) *Crawler {
	// ToDo: Improve ugly default parameters (variadic functions?)

	c := &Crawler{Domains: domains}

	if domains == nil {
		panic("You need to specify domains")
	}
	c.Domains = domains

	if crawlThreads == 0 {
		crawlThreads = 4
	}
	c.CrawlThreads = crawlThreads

	c.Storage = storage.New()

	return c
}

func (c Crawler) Run() {

	// Instantiate default collector
	collector := colly.NewCollector(
		// MaxDepth is 1, so only the links on the scraped page are visited
		colly.MaxDepth(1),
		colly.Async(true),
		colly.IgnoreRobotsTxt(),
		//colly.AllowedDomains(domains...),
	)

	collector.SetRequestTimeout(3 * time.Second)

	// Limit the maximum parallelism to eg. 2
	// This is necessary if the goroutines are dynamically
	// created to control the limit of simultaneous requests.
	collector.Limit(
		&colly.LimitRule{DomainGlob: "*", Parallelism: c.CrawlThreads},
	)

	//collector.WithTransport(&http.Transport{
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

	collector.OnRequest(func(r *colly.Request) {
		r.Headers.Set("Accept-Language", "de;q=1, en;q=0.9")
		fmt.Println("visiting", r.URL)
	})

	collector.OnResponse(func(r *colly.Response) {
		// Store the result
		pageUrl, err := url.Parse(r.Request.URL.String())
		if err != nil {
			println(err)
			return
		}
		ctxPageType := r.Ctx.GetAny("pageType")
		ctxOriginalDomain := r.Ctx.Get("originalDomain")
		pageType := page.TypeFromInterface(ctxPageType)

		c.Storage.StorePageVisit(ctxOriginalDomain, pageUrl, r.Body, pageType)
	})

	collector.OnHTML("a[href]", func(e *colly.HTMLElement) {
		// Check whether we should follow the found href
		if !utils.IsExternalLink(e) && utils.IsMeaningfulLink(e) {
			linkText := utils.CleanLinkText(e.Text)
			linkHref := e.Attr("href")
			pageType := page.GetEstimatedPageTypeOfLink(linkText, linkHref)
			if pageType != page.UnknownPage {
				fullUrl, err := utils.LinkToAbsoluteUrl(e)
				if err != nil {
					return
				}
				// Visit link found on page on a new thread
				//e.Request.Visit(sanitizedUrl)  // Doesn't seem to work
				origCtx := e.Request.Ctx
				ctx := colly.NewContext()
				ctx.Put("originalDomain", string(origCtx.Get("originalDomain")))
				ctx.Put("pageType", int(pageType))
				collector.Request("GET", fullUrl, nil, ctx, nil)
			}
		}
	})

	collector.OnError(func(r *colly.Response, e error) {
		fmt.Println("error visiting", r.Request.URL, e)
	})

	for _, domain := range c.Domains {
		ctx := colly.NewContext()
		ctx.Put("originalDomain", string(domain))
		ctx.Put("pageType", int(page.IndexPage))
		collector.Request("GET", utils.SanitizeUrlToCrawl(domain), nil, ctx, nil)
	}

	collector.Wait()
	c.Storage.Wait()
	//c.TearDown()  // ToDo: Doesn't work currently
}

func (c *Crawler) TearDown() {
	// ToDo: Call this method on on ctrl-C interrupt signal
	c.Storage.TearDown()
}
