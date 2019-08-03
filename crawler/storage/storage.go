package storage

import (
	"fmt"
	"net/url"
	"os"
	"path/filepath"

	"github.com/gosimple/slug"
)

type CrawledPage struct {
	domain string
}

var (
	outputPath = "../output"
)

func pathToFolderName(path string) string {
	return slug.Make(path)
}

func StorePageVisit(url *url.URL, body []byte) {
	// ToDo: 1. Store HTML files, 2. Append meta data to JSON file?
	// Setup directory structure
	domainDirectory := filepath.Join(outputPath, url.Host)
	pageDirectory := filepath.Join(domainDirectory, pathToFolderName(url.Path))
	// Create directory structure if it does not exist
	err := os.MkdirAll(pageDirectory, os.ModePerm)
	if err != nil {
		fmt.Println(err)
		return
	}

	// Write html file
	filePath := filepath.Join(pageDirectory, filepath.Base("content.html"))
	f, err := os.Create(filePath)
	if err != nil {
		fmt.Println(err)
		return
	}

	_, err = f.Write(body)
	if err != nil {
		fmt.Println(err)
		f.Close()
		return
	}
}
