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
	href := trimUrlStr(link.Attr("href"))
	hrefUrl, err := url.Parse(href)
	if err != nil {
		fmt.Println("LinkToAbsoluteUrl. Request URL: " + link.Request.URL.String())
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
		resolvedUrl := trimUrlStr(requestUrl.ResolveReference(hrefUrl2).String())
		return resolvedUrl, nil
	} else {
		return trimUrlStr(hrefUrl.String()), nil
	}
}

func IsExternalLink(link *colly.HTMLElement) (bool, error) {
	hrefUrl, err := url.Parse(trimUrlStr(link.Attr("href")))
	if err != nil {
		return true, err
	}
	// Relative urls are definitely no external urls
	if !hrefUrl.IsAbs() {
		return false, nil
	}
	return hrefUrl.Host != link.Request.URL.Host, nil
}

// CleanLinkText Strips away html tags (eg. img), removes new lines and strips whitespaces
func CleanLinkText(linkText string) string {
	p := bluemonday.StrictPolicy()
	san := p.Sanitize(linkText)
	trimmed := strings.TrimSpace(strings.ReplaceAll(san, "\n", ""))
	return trimmed
}

// IsTextLink returns true if the href is not # or a javascript call.
// It also makes sure that the the body of the a element contains text, not only images
func IsTextLink(link *colly.HTMLElement) bool {
	// Validate href target
	href := trimUrlStr(link.Attr("href"))
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

// Trim \r\n, \n, \t and whitespace from the URL
func trimUrlStr(s string) string {
	return strings.ReplaceAll(
		strings.ReplaceAll(
			strings.ReplaceAll(
				strings.ReplaceAll(
					s, "\r\n", ""),
				"\n", ""),
			"\t", ""),
		" ", "")
}
