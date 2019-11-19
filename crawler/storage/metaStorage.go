package storage

import (
	"encoding/json"
	"io/ioutil"
	"net/url"

	"crawler/page"
)

type crawlerMetaData struct {
	CrawledPages []crawledPage `json:"crawledPages"`
}

type crawledPage struct {
	OriginalDomain     string `json:"originalDomain"`
	ActualDomain       string `json:"actualDomain"` // In case the crawled domain redirect"
	PageTypeIdentifier string `json:"pageType"`
	Url                string `json:"url"`
	HtmlFilePath       string `json:"htmlFilePath"`
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

func (s *Storage) writeCrawlerMetaDataToFile() {
	if s == nil {
		s.logger.Errorw("Error writing meta data to file. The storage object is nil")
		return
	}

	if s.metaData == nil {
		s.logger.Errorw("Error writing meta data to file. The metaData object is nil")
		return
	}

	jsonData, err := json.MarshalIndent(s.metaData, "", "  ")
	if err != nil {
		s.logger.Errorw("Error serializing crawler meta data to json",
			"error", err,
		)
		return
	}
	err = ioutil.WriteFile(s.metaDataFile, jsonData, 0644)
	if err != nil {
		s.logger.Errorw("Unable to write meta data json file",
			"error", err,
		)
		return
	}
}

func (s *Storage) updateCrawlerMetaData(domain string, url *url.URL, pageType page.Type) {
	newPage := crawledPage{
		OriginalDomain:     domain,
		ActualDomain:       url.Hostname(),
		HtmlFilePath:       s.getHtmlFilePathForPage(domain, pageType),
		PageTypeIdentifier: pageType.StringIdentifier(),
		Url:                url.String(),
	}
	//s.lock.Lock()
	s.metaData.CrawledPages = append(s.metaData.CrawledPages, newPage)
	//s.lock.Unlock()
}
