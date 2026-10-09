from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeToJson
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IJSONSummarySerializerMetadata)
class JSONSummarySerializerMetadata:
    """Additional metadata to be exposed on listings."""

    def default_metadata_fields(self):
        return {"image_field", "image_scales", "effective", "Subject"}


@implementer(ISerializeToJson)
@adapter(IDexterityContent, Interface)
class MembersOnlySerializeToJson(SerializeToJson):
    """Serialiser that returns only teaser fields for anonymous users
    when content is in the members_only workflow state."""

    TEASER_FIELDS = {
        "title",
        "description",
        "preview_image",
        "preview_image_link",
        "effective",
        "creators",
    }

    def _is_members_only(self, obj):
        wf_tool = getToolByName(obj, "portal_workflow")
        state = wf_tool.getInfoFor(obj, "review_state", None)
        return state == "members_only"

    def _can_view(self, obj):
        from AccessControl import getSecurityManager

        return bool(getSecurityManager().checkPermission("View", obj))

    def _is_anonymous(self):
        from AccessControl import getSecurityManager

        user = getSecurityManager().getUser()
        return user.getUserName() == "Anonymous User"

    def __call__(self, version=None, include_items=True, include_expansion=True):
        result = super().__call__(
            version=version,
            include_items=include_items,
            include_expansion=include_expansion,
        )

        obj = self.context

        # Not "is anonymous": logged-in people may lack access too, when
        # content is shared with some groups only.
        if self._is_members_only(obj) and not self._can_view(obj):
            teaser = {
                "@id": result.get("@id"),
                "@type": result.get("@type"),
                "type_title": result.get("type_title"),
                "review_state": result.get("review_state"),
                "is_members_only": True,
            }
            for field in self.TEASER_FIELDS:
                if field in result:
                    teaser[field] = result[field]
            return teaser

        return result
