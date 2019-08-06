package storage

import (
	"net/url"
	"os"
	"path/filepath"
	"sync"

	"crawler/page"
)

type Storage struct {
	// ToDo: Lock for metaData
	metaData     crawlerMetaData
	outputPath   string
	metaDataFile string
	wg           *sync.WaitGroup
	lock         *sync.RWMutex
}

func New() *Storage {
	// ToDo Allow adding options?
	s := &Storage{}
	s.wg = &sync.WaitGroup{}
	s.lock = &sync.RWMutex{}

	// Set defaults
	s.outputPath = "output"
	s.metaDataFile = filepath.Join(s.outputPath, filepath.Base("crawler.json"))

	return s
}

// Wait returns when the Storage jobs are finished
func (s *Storage) Wait() {
	s.wg.Wait()
}

func (s *Storage) StorePageVisit(originalDomain string, url *url.URL, body []byte, pageType page.Type) {

	if originalDomain == "" {
		panic("Storage domain is not specified")
	}

	s.wg.Add(1)
	go s.storePageVisit(originalDomain, url, body, pageType)
}

func (s *Storage) storePageVisit(originalDomain string, url *url.URL, body []byte, pageType page.Type) {
	defer s.wg.Done()

	// Create output directory if it does not exist
	err := os.MkdirAll(s.outputPath, os.ModePerm)
	if err != nil {
		panic(err)
	}

	s.storePageHtml(originalDomain, body, pageType)

	s.updateCrawlerMetaData(url.Hostname(), url, pageType)
	s.writeCrawlerMetaDataToFile()
	// Update storage every 100 crawled pages (trade off between unneeded
	//if len(s.metaData.CrawledPages) % 100 == 0 {
	//    s.writeCrawlerMetaDataToFile()
	//}
}

func (s *Storage) getHtmlFilePathForPage(domain string, pageType page.Type) string {
	return filepath.Join(s.outputPath, domain, pageType.StringIdentifier(), "index.html")
}

// TearDown can be used to do storage tidy-up tasks after the crawling is done
func (s *Storage) TearDown() {
	s.writeCrawlerMetaDataToFile()
}
