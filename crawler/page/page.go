package page

import (
	"strings"
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
func GetEstimatedPageTypeOfLink(linkText, linkTarget string) Type {
	wordToTypeMap := map[string]Type{
		"privacy":     PrivacyPage,
		"datenschutz": PrivacyPage,

		"contact": ContactPage,
		"kontakt": ContactPage,

		"imprint":   ImprintPage,
		"impressum": ImprintPage,

		//"terms and conditions": TermsPage,
		//"terms &amp; conditions": TermsPage,
		//"agb": TermsPage,
	}

	// Identify page by
	var estimatedPageType = UnknownPage
	for searchTerm, pageType := range wordToTypeMap {
		if strings.Contains(strings.ToLower(linkText), searchTerm) {
			estimatedPageType = pageType
			break
		}
	}

	// ToDo: check linkTarget and return if it comes to the same estimation as linkText

	return estimatedPageType
}
