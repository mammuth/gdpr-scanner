package storage

import (
	"net/url"
	"os"
	"path/filepath"

	"crawler/page"
)

const (
	outputPath = "output"
)

type Storage struct {
	metaData crawlerMetaData
}

func (storage *Storage) StorePageVisit(url *url.URL, body []byte, pageType page.Type) {
	// ToDo: Make async
	// ToDo: Periodically write meta data to file to avoid data loss
	// ToDo: Pass crawledDomain via request context and use it next to the url host (to differentiate wanted and actual domain in case of redirects)

	// Create output directory if it does not exist
	err := os.MkdirAll(outputPath, os.ModePerm)
	if err != nil {
		panic(err)
	}

	domain := url.Hostname()
	storage.storePageHtml(domain, body, pageType)
	storage.updateCrawlerMetaData(url.Hostname(), url, pageType)
}

func getHtmlFilePathForPage(domain string, pageType page.Type) string {
	return filepath.Join(outputPath, domain, pageType.StringIdentifier(), "content.html")
}

// NotifyCrawlingFinished can be used to do storage tidy-up tasks after the crawling is done
func (storage *Storage) NotifyCrawlingFinished() {
	storage.writeCrawlerMetaDataToFile()
}
