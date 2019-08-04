package utils

import (
	"fmt"
	"net/url"

	"github.com/gocolly/colly"
)

func LinkToAbsoluteUrl(link *colly.HTMLElement) (absoluteUrl string, err error) {
	href := link.Attr("href")
	hrefUrl, err := url.Parse(href)
	if err != nil {
		fmt.Println(err)
		return href, error(err)
	}
	if hrefUrl.IsAbs() {
		return hrefUrl.String(), nil
	} else {
		requestUrl := link.Request.URL
		return requestUrl.ResolveReference(hrefUrl).String(), nil
	}
}

func IsExternalLink(link *colly.HTMLElement) bool {
	hrefUrl, err := url.Parse(link.Attr("href"))
	if err != nil {
		fmt.Println(err)
		return true
	}
	// Relative urls are definitely no external urls
	if !hrefUrl.IsAbs() {
		return false
	}
	return hrefUrl.Host != link.Request.URL.Host
}
