package page

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

// Converts string or int values to Type
func TypeFromInterface(i interface{}) Type {
	integer := i.(int)
	integer, ok := i.(int)
	if !ok {
		return UnknownPage
	}
	return Type(integer)
}
