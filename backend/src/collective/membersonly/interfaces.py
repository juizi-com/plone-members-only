"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


from dataclasses import dataclass  # noqa: E402
from collections.abc import Callable  # noqa: E402
from zope.interface import Interface  # noqa: E402


class IAccessMessage(Interface):
    """What a visitor sees on members-only content they can't read.

    Register one (unnamed) utility to replace the default, which is the
    login prompt for anonymous visitors and "you don't have access" for
    logged-in people. collective.membership provides one with plan names
    and links to joining or the member dashboard.
    """

    def __call__(context, request):
        """Return {'text': str, 'actions': [{'label': str, 'url': str}]}
        or None for the default. Never reveal who else can see it."""


@dataclass(frozen=True)
class TeaserField:
    """A field another add-on offers for the public teaser.

    name: the key in the teaser. It can't replace anything the teaser
        already has.
    label: how the settings panel lists it.
    default: whether it's in the teaser until an admin says otherwise.
    never_public: refuse the field. It's left out of the settings panel and
        out of the teaser whatever is stored, whoever else offers it, even a
        built-in field. Use it for files.
    serialize: called with (context, request), returns something JSON
        compatible. An empty result leaves the field out. Without it, the
        attribute of that name is used.
    """

    name: str
    label: str = ""
    default: bool = False
    never_public: bool = False
    serialize: Callable | None = None


class ITeaserFieldProvider(Interface):
    """Offers fields for the public teaser. Register as a named utility.

    Utilities are per instance and one instance can host several sites, so a
    provider says which fields apply to the site it's asked about.
    """

    def fields(site):
        """Return the TeaserFields for this site: none if the add-on isn't
        installed on it."""
