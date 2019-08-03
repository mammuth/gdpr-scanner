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
