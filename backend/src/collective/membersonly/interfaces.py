"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


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
