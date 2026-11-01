from collective.membersonly.access import is_members_only
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer


@indexer(IDexterityContent)
def members_only(obj):
    """For listings: lets a card show a badge with no request per item."""
    return is_members_only(obj)
