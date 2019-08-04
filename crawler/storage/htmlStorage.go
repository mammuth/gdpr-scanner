package storage

import (
	"os"
	"path/filepath"

	"crawler/page"
)

func (storage *Storage) storePageHtml(domain string, body []byte, pageType page.Type) {
	filePath := getHtmlFilePathForPage(domain, pageType)

	// Create directory structure if it does not exist
	err := os.MkdirAll(filepath.Dir(filePath), os.ModePerm)
	if err != nil {
		panic(err)
	}

	// Write html file
	f, err := os.Create(filePath)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	_, err = f.Write(body)
	if err != nil {
		panic(err)
	}
}
