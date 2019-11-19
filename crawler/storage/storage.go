package storage

import (
	"net/url"
	"os"
	"path/filepath"
	"strconv"

	"go.uber.org/zap"

	"crawler/page"
)

type Storage struct {
	metaData     *crawlerMetaData
	outputPath   string
	metaDataFile string
	logger       *zap.SugaredLogger
	//wg           *sync.WaitGroup
	//lock         *sync.RWMutex
}

func New(logger *zap.SugaredLogger) *Storage {
	// ToDo Allow adding options?
	s := &Storage{
		metaData: &crawlerMetaData{},
		logger:   logger,
	}
	//s.wg = &sync.WaitGroup{}
	//s.lock = &sync.RWMutex{}

	// Set defaults
	s.outputPath = "output"
	s.metaDataFile = filepath.Join(s.outputPath, filepath.Base("crawler.json"))

	return s
}

// Wait returns when the Storage jobs are finished
//func (s *Storage) Wait() {
//	s.wg.Wait()
//}

func (s *Storage) StorePageVisit(originalDomain string, url *url.URL, body []byte, pageType page.Type) {

	if originalDomain == "" {
		s.logger.Errorw("Storage domain is not specified",
			"url", url,
		)
		return
	}

	//s.wg.Add(1)
	//go s.storePageVisit(originalDomain, url, body, pageType)
	s.storePageVisit(originalDomain, url, body, pageType)
}

// AlreadyStored returns a boolean indicating whether the given URL is already stored
func (s *Storage) AlreadyStored(url *url.URL) bool {
	for _, v := range s.metaData.CrawledPages {
		if v.Url == url.String() {
			return true
		}
	}
	return false
}

func (s *Storage) storePageVisit(originalDomain string, url *url.URL, body []byte, pageType page.Type) {
	//defer s.wg.Done()

	// Create output directory if it does not exist
	err := os.MkdirAll(s.outputPath, os.ModePerm)
	if err != nil {
		s.logger.Errorw("Error creating the output directory",
			"outputPath", s.outputPath,
		)
		panic(err)
	}

	s.storePageHtml(originalDomain, body, pageType)

	s.updateCrawlerMetaData(originalDomain, url, pageType)
	s.writeCrawlerMetaDataToFile()
	// Update storage every 100 crawled pages (trade off between unneeded
	//if len(s.metaData.CrawledPages) % 100 == 0 {
	//    s.writeCrawlerMetaDataToFile()
	//}
}

// Relative path (as seen from crawler.json meta data file) to the html file of the given page
// Handles multiple pages of the same type by creating subdirectories for each page
func (s *Storage) getHtmlFilePathForPage(domain string, pageType page.Type) string {
	num := s.GetNumberOfCrawledPagesForDomainOfType(domain, pageType)
	prefix := "1"
	if num > 0 {
		prefix = strconv.Itoa(num + 1)
	}
	return filepath.Join(domain, pageType.StringIdentifier(), prefix, "index.html")
}

// TearDown can be used to do storage tidy-up tasks after the crawling is done
func (s *Storage) TearDown() {
	//s.writeCrawlerMetaDataToFile()
}

func (s *Storage) GetNumberOfCrawledDomains() int {
	domains := map[string]bool{}
	for _, p := range s.metaData.CrawledPages {
		domains[p.OriginalDomain] = true
	}
	return len(domains)
}

func (s *Storage) GetNumberOfCrawledPages() int {
	return len(s.metaData.CrawledPages)
}

func (s *Storage) GetNumberOfCrawledPagesForDomain(domain string) (count int) {
	for _, s := range s.metaData.CrawledPages {
		if s.OriginalDomain == domain {
			count += 1
		}
	}
	return
}

func (s *Storage) GetNumberOfCrawledPagesForDomainOfType(domain string, pageType page.Type) (count int) {
	for _, s := range s.metaData.CrawledPages {
		if s.OriginalDomain == domain && s.PageTypeIdentifier == pageType.StringIdentifier() {
			count += 1
		}
	}
	return
}
