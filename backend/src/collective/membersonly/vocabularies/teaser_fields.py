from collective.membersonly.views.teaser import offered_fields
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@provider(IVocabularyFactory)
def teaser_fields_vocabulary(context):
    """Built-in fields and what other add-ons offer on this site."""
    return SimpleVocabulary([
        SimpleTerm(name, name, label) for name, label in offered_fields()
    ])
