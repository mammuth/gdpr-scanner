package storage

import (
	"os"
	"path/filepath"

	"crawler/page"
)

func (s *Storage) storePageHtml(domain string, body []byte, pageType page.Type) {
	filePath := s.getHtmlFilePathForPage(domain, pageType)

	// Create directory structure if it does not exist
	err := os.MkdirAll(filepath.Dir(filePath), os.ModePerm)
	if err != nil {
		panic(err)
	}

	// Write html file
	f, err := os.Create(filePath)
	if err != nil {
		s.logger.Errorw("Unable to create HTML file",
			"error", err,
			"domain", domain,
		)
	}
	defer f.Close()

	_, err = f.Write(body)
	if err != nil {
		s.logger.Errorw("Unable to write HTML to file",
			"error", err,
			"domain", domain,
		)
	}
}
