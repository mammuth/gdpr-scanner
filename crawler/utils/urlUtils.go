package utils

import (
	"fmt"
	"net/url"
	"strings"

	"github.com/gocolly/colly"
	"github.com/microcosm-cc/bluemonday"
)

// LinkToAbsoluteUrl resolves a href target to an absolute URL
// Attention: All relative links are simply assumed to be document-root-based relative urls!
// Thus, href="privacy/" becomes href="/privacy"
func LinkToAbsoluteUrl(link *colly.HTMLElement) (absoluteUrl string, err error) {
	// ToDo: Only convert relative URL to document-root-based URI IFF the "correct" relative URL fails to download
	href := link.Attr("href")
	hrefUrl, err := url.Parse(href)
	if err != nil {
		fmt.Println(err)
		return href, error(err)
	}
	if !hrefUrl.IsAbs() {
		// Attention: Unexpected things ahead
		// many pages use relative urls wrongly:
		// (eg. href="privacy" on domain.com/page/ which leads to 404 on domain.com/page/privacy)
		// This is why we assume href="privacy/" to actually mean href="/privacy". This will raise false negatives, but probably less than the other way around
		hrefUrlStr := href
		if !strings.HasPrefix(hrefUrlStr, "/") && !strings.HasPrefix(hrefUrlStr, "#") {
			hrefUrlStr = "/" + hrefUrlStr
		}
		hrefUrl2, err := url.Parse(hrefUrlStr)
		if err != nil {
			fmt.Println(err)
			return hrefUrlStr, error(err)
		}
		requestUrl := link.Request.URL
		resolvedUrl := strings.TrimSpace(requestUrl.ResolveReference(hrefUrl2).String())
		return resolvedUrl, nil
	} else {
		return hrefUrl.String(), nil
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
	if strings.HasPrefix(href, "#") || strings.HasPrefix(href, "javascript:") {
		return false
	}

	// Validate link text
	san := CleanLinkText(link.Text)
	if san == "" {
		return false
	}
	return true
}

func SanitizeUrlToCrawl(inputUrl string) string {
	if !strings.HasPrefix(inputUrl, "http") {
		return "http://" + inputUrl
	}
	return inputUrl
}
