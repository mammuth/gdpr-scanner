package storage

import (
	"io/ioutil"
	"os"
	"path/filepath"

	"crawler/page"
)

func (s *Storage) storePageHtml(domain string, body []byte, pageType page.Type) {
	filePath := filepath.Join(s.outputPath, s.getHtmlFilePathForPage(domain, pageType))

	// Create directory structure if it does not exist
	err := os.MkdirAll(filepath.Dir(filePath), os.ModePerm)
	if err != nil {
		panic(err)
	}

	err = ioutil.WriteFile(filePath, body, 0644)
	if err != nil {
		s.logger.Errorw("Unable to write HTML file",
			"error", err,
			"domain", domain,
		)
	}
}
