package storage

import (
	"crawler/page"
	"encoding/json"
	"io/ioutil"
	"net/url"
	"path/filepath"
)

type crawlerMetaData struct {
	CrawledPages []crawledPage `json:"crawledPages"`
}

var metaDataFilePath = filepath.Join(outputPath, filepath.Base("crawler.json"))

//var (
//	crawlerMetaDataInstance *crawlerMetaData
//	once sync.Once
//)
//func getCrawlerMetaDataSingleton() *crawlerMetaData {
//	once.Do(func() {
//		crawlerMetaDataInstance = &crawlerMetaData{}
//	})
//	return crawlerMetaDataInstance
//}

type crawledPage struct {
	CrawledDomain      string `json:"crawledDomain"`
	ActualDomain       string `json:"actualDomain"` // In case the crawled domain redirect"
	HtmlFilePath       string `json:"htmlFilePath"`
	PageTypeIdentifier string `json:"pageType"`
	Url                string `json:"url"`
}

// Reads the current meta data json file and returns it as a struct
//func (storage *Storage) getCrawlerMetaDataFromFile() crawlerMetaData {
//	tmpData := crawlerMetaData{}
//	jsonText, err := ioutil.ReadFile(metaDataFilePath)
//	if err != nil {
//		fmt.Println(err)
//	}
//	err = json.Unmarshal(jsonText, &tmpData)
//	if err != nil {
//		fmt.Println(err)
//	}
//	return tmpData
//}

func (storage Storage) writeCrawlerMetaDataToFile() {
	jsonData, err := json.MarshalIndent(storage.metaData, "", "  ")
	if err != nil {
		panic(err)
	}
	err = ioutil.WriteFile(metaDataFilePath, jsonData, 0644)
	if err != nil {
		panic(err)
	}
}

func (storage *Storage) updateCrawlerMetaData(domain string, url *url.URL, pageType page.Type) {
	newPage := crawledPage{
		CrawledDomain:      domain,
		ActualDomain:       url.Hostname(),
		HtmlFilePath:       getHtmlFilePathForPage(domain, pageType),
		PageTypeIdentifier: pageType.StringIdentifier(),
		Url:                url.String(),
	}
	storage.metaData.CrawledPages = append(storage.metaData.CrawledPages, newPage)
}
