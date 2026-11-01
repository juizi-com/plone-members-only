from collective.membersonly.interfaces import IBrowserLayer
from plone import api
from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from zope.component import getAllUtilitiesRegisteredFor
from zope.globalrequest import getRequest
from zope.interface import implementer


# plone.restapi fills this one in itself, with no column and no accessor.
BUILT_IN = {"type_title"}


def _collect(method):
    """The names every registered utility gives from `method`."""
    names = set()
    for utility in getAllUtilitiesRegisteredFor(IJSONSummarySerializerMetadata):
        names.update(getattr(utility, method, tuple)())
    return names


@implementer(IJSONSummarySerializerMetadata)
class JSONSummarySerializerMetadata:
    """Additional metadata to be exposed on listings."""

    def default_metadata_fields(self):
        return {"image_field", "image_scales", "effective", "Subject", "members_only"}

    def blocklisted_attributes(self):
        """Fields another add-on lists by default that this site's catalog has
        no column for, which happens when a package is loaded for the whole
        process but not installed on this site, or its upgrade hasn't run.

        Gated items are in visitors' listings, and a field with no column
        wakes the item. Waking a gated item as a visitor raises Unauthorized,
        which loses the whole listing, not just the field.
        """
        if not IBrowserLayer.providedBy(getRequest()):
            return set()
        columns = set(api.portal.get_tool("portal_catalog").schema())
        answered_elsewhere = (
            BUILT_IN
            | _collect("non_metadata_attributes")
            | _collect("field_accessors")
        )
        return _collect("default_metadata_fields") - columns - answered_elsewhere

