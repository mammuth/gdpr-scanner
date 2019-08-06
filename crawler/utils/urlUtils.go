package utils

import (
	"fmt"
	"net/url"
	"strings"

	"github.com/gocolly/colly"
	"github.com/microcosm-cc/bluemonday"
)

func LinkToAbsoluteUrl(link *colly.HTMLElement) (absoluteUrl string, err error) {
	href := link.Attr("href")
	hrefUrl, err := url.Parse(href)
	hrefUrl.RequestURI()
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

// CleanLinkText Strips away html tags (eg. img), removes new lines and strips whitespaces
func CleanLinkText(linkText string) string {
	p := bluemonday.StrictPolicy()
	san := p.Sanitize(linkText)
	trimmed := strings.TrimSpace(strings.ReplaceAll(san, "\n", ""))
	return trimmed
}

// IsMeaningfulLink returns true if the href is not # or a javascript call.
// It also makes sure that the the body of the a element contains text, not only images
func IsMeaningfulLink(link *colly.HTMLElement) bool {
	// Validate href target
	href := link.Attr("href")
	if href == "#" || strings.HasPrefix(href, "javascript:") {
		return false
	}

	// Validate link text
	san := CleanLinkText(link.Text)
	if san == "" {
		return false
	}
	return true
}
