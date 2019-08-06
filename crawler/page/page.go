package page

import (
	"strings"

	"github.com/gocolly/colly"
)

// Type defines some well-known page types like index page, contact page or privacy policy
type Type int

const (
	UnknownPage Type = iota
	IndexPage        = iota
	PrivacyPage      = iota
	TermsPage        = iota
	ContactPage      = iota
	ImprintPage      = iota
)

func (t Type) String() string {
	return [...]string{"Unknown page", "Index page", "Privacy statement", "Terms page", "Contact page", "Imprint"}[t]
}

func (t Type) StringIdentifier() string {
	return [...]string{"unknown", "index", "privacy", "terms", "contact", "imprint"}[t]
}

// TypeFromInterface converts int values to Type
func TypeFromInterface(i interface{}) Type {
	integer, ok := i.(int)
	if !ok {
		return UnknownPage
	}
	return Type(integer)
}

// GetEstimatedPageTypeOfLink returns the estimated type of the link, based on url and text
func GetEstimatedPageTypeOfLink(link *colly.HTMLElement) Type {
	// ToDo: Refactor to avoid those nasty loops. Maybe use a map[string][Type]?
	privacyWords := []string{"privacy", "datenschutz"}
	imprintWords := []string{"imprint", "impressum"}
	contactWords := []string{"contact", "kontakt"}
	termsWords := []string{"agb", "terms and conditions"}

	linkText := strings.ToLower(link.Text)
	//urlPath := strings.ToLower(link.Request.URL.Path)
	for _, word := range privacyWords {
		if strings.Contains(linkText, word) {
			return PrivacyPage
		}
	}

	for _, word := range imprintWords {
		if strings.Contains(linkText, word) {
			return ImprintPage
		}
	}

	for _, word := range termsWords {
		if strings.Contains(linkText, word) {
			return TermsPage
		}
	}

	for _, word := range contactWords {
		if strings.Contains(linkText, word) {
			return ContactPage
		}
	}

	return UnknownPage
}
