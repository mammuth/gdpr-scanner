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

// GetEstimatedPageTypesOfLink returns the estimated type of the link, based on url and text
func GetEstimatedPageTypeOfLink(linkText, linkTarget string) Type {
	// ToDo: Return []Type and store the page for both types
	// ToDo: Somehow avoid flagging eg. PDF links as Privacy Policy and store them as HTML (not sure right now where to handle this)
	wordToTypeMap := map[string]Type{
		"privacy":     PrivacyPage,
		"datenschutz": PrivacyPage,
		//"privacy policy":        PrivacyPage,
		//"privacy-policy":        PrivacyPage,
		//"privacypolicy":         PrivacyPage,
		//"privacy statement":     PrivacyPage,
		//"privacy-statement":     PrivacyPage,
		//"privacystatement":      PrivacyPage,
		//"statement of privacy":  PrivacyPage,
		//"statement for privacy": PrivacyPage,
		//"about privacy":         PrivacyPage,
		//"how we do privacy":     PrivacyPage,
		//"datenschutzerklärung":           PrivacyPage,

		"contact": ContactPage,
		"kontakt": ContactPage,

		//"imprint":   ImprintPage,
		//"impressum": ImprintPage,

		//"terms and conditions": TermsPage,
		//"terms &amp; conditions": TermsPage,
		//"agb": TermsPage,
	}

	var possibleTypes []Type

	for searchTerm, pageType := range wordToTypeMap {
		//if strings.ToLower(linkText) == searchTerm {
		if strings.Contains(strings.ToLower(linkText), searchTerm) {
			possibleTypes = append(possibleTypes, pageType)
		}
	}
	if len(possibleTypes) > 0 {
		return possibleTypes[0]
	}
	return UnknownPage
}
