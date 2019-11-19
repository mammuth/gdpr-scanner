package crawl

import (
	"net/url"
	"time"

	"github.com/gocolly/colly"
	"go.uber.org/zap"

	"crawler/page"
	"crawler/storage"
	"crawler/utils"
)

type Crawler struct {
	Domains         []string
	CrawlThreads    int
	Storage         *storage.Storage
	unsugaredLogger *zap.Logger
	logger          *zap.SugaredLogger
	collector       *colly.Collector
	lastProgressLog time.Time
}

func New(domains []string, crawlThreads int, verbose bool) *Crawler {
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

	//c.unsugaredLogger, _ = zap.NewProduction()
	if verbose == true {
		c.unsugaredLogger, _ = zap.NewDevelopment()
	} else {
		loggerConfig := zap.Config{
			Level:            zap.NewAtomicLevelAt(zap.InfoLevel),
			Development:      false,
			Encoding:         "console",
			EncoderConfig:    zap.NewDevelopmentEncoderConfig(),
			OutputPaths:      []string{"stderr"},
			ErrorOutputPaths: []string{"stderr"},
		}
		c.unsugaredLogger, _ = loggerConfig.Build()
	}
	defer c.unsugaredLogger.Sync() // flushes buffer, if any
	c.logger = c.unsugaredLogger.Sugar()

	c.Storage = storage.New(c.logger)

	c.collector = colly.NewCollector(
		// MaxDepth is 1, so only the links on the scraped page are visited
		colly.MaxDepth(1),
		colly.Async(true),
		colly.IgnoreRobotsTxt(),
		//colly.AllowedDomains(domains...),
	)

	return c
}

func (c *Crawler) Run() {
	c.collector.SetRequestTimeout(6 * time.Second)

	// Limit the maximum parallelism to eg. 2
	// This is necessary if the goroutines are dynamically
	// created to control the limit of simultaneous requests.
	c.collector.Limit(
		&colly.LimitRule{DomainGlob: "*", Parallelism: c.CrawlThreads},
	)

	//c.collector.WithTransport(&http.Transport{
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

	c.collector.OnRequest(func(r *colly.Request) {
		if c.Storage.AlreadyStored(r.URL) {
			c.logger.Debugw("Skipping url because it's already visited",
				"url", r.URL,
			)
			return
		}

		r.Headers.Set("Accept-Language", "de;q=1, en;q=0.9")
		r.Headers.Set("Header", "Friendly GDPR compliance scanner (https://github.com/mammuth/gdpr-scanner/")
		c.logger.Debugw("Visiting url",
			"url", r.URL,
		)
	})

	c.collector.OnResponse(func(r *colly.Response) {
		// Store the result
		pageUrl, err := url.Parse(r.Request.URL.String())
		if err != nil {
			c.logger.Debugw("Error parsing response",
				"url", r.Request.URL,
				"statusCode", r.StatusCode,
				"headers", r.Headers,
				"body", r.Body,
			)
			return
		}
		ctxPageType := r.Ctx.GetAny("pageType")
		ctxOriginalDomain := r.Ctx.Get("originalDomain")
		pageType := page.TypeFromInterface(ctxPageType)

		c.Storage.StorePageVisit(ctxOriginalDomain, pageUrl, r.Body, pageType)

		// Log progress
		now := time.Now()
		if now.After(c.lastProgressLog.Add(30 * time.Second)) {
			c.lastProgressLog = now
			crawledDomains := c.Storage.GetNumberOfCrawledDomains()
			crawledPages := c.Storage.GetNumberOfCrawledPages()
			c.logger.Infow("Progress Update",
				"crawledDomains", crawledDomains,
				"crawledPages", crawledPages,
				"lastDomain", ctxOriginalDomain,
			)
		}
	})

	c.collector.OnHTML("a[href]", func(e *colly.HTMLElement) {
		domain := e.Request.Ctx.Get("originalDomain")
		// Check whether we should follow the found href
		isExternal, err := utils.IsExternalLink(e)
		if err != nil {
			c.logger.Debugw("Cannot specify whether link is external or not.",
				"originalDomain", domain,
				"error", err,
			)
		}
		if !isExternal && utils.IsTextLink(e) {
			linkText := utils.CleanLinkText(e.Text)
			linkHref := e.Attr("href")
			pageType := page.GetEstimatedPageTypeOfLink(linkText, linkHref)
			if pageType != page.UnknownPage {
				domain := e.Request.Ctx.Get("originalDomain")
				if c.Storage.GetNumberOfCrawledPagesForDomain(domain) >= 30 {
					c.logger.Debugw(
						"Don't queue next page visit since we reached the page limit for this domain",
						"domain", domain,
						"url", linkHref,
					)
					return
				}
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
				err = c.collector.Request("GET", fullUrl, nil, ctx, nil)
				if err != nil {
					c.logger.Debugw("Error queuing a request",
						"domain", domain,
						"url", fullUrl,
						"error", err,
					)
				}
			}
		}
	})

	c.collector.OnError(func(r *colly.Response, e error) {
		c.logger.Debugw("Error visiting url",
			"url", r.Request.URL,
			"error", e,
			"statusCode", r.StatusCode,
			"headers", r.Headers,
		)
	})

	startTime := time.Now()
	c.logger.Infow("Crawler started",
		"time", startTime.String(),
		"rawTime", startTime,
	)

	for _, domain := range c.Domains {
		ctx := colly.NewContext()
		ctx.Put("originalDomain", string(domain))
		ctx.Put("pageType", int(page.IndexPage))
		c.collector.Request("GET", utils.SanitizeUrlToCrawl(domain), nil, ctx, nil)
	}

	c.collector.Wait()
	//c.Storage.Wait()
	//c.TearDown()  // ToDo: Doesn't work currently

	elapsedTime := time.Since(startTime)
	c.logger.Infow("Crawler finished",
		"duration", elapsedTime.String(),
		"crawledDomains", c.Storage.GetNumberOfCrawledDomains(),
		"crawledPages", c.Storage.GetNumberOfCrawledPages(),
	)
}

func (c *Crawler) TearDown() {
	// ToDo: Call this method on on ctrl-C interrupt signal
	c.Storage.TearDown()
}
