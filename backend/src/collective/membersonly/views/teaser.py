from Acquisition import aq_base
from collective.membersonly.access import access_info
from collective.membersonly.access import access_message
from collective.membersonly.interfaces import ITeaserFieldProvider
from plone import api
from plone.namedfile.scaling import ImageScaling
from plone.registry.interfaces import IRegistry
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging


logger = logging.getLogger("collective.membersonly")

KNOWN_RECORD = "collective.membersonly.teaser_state.known"

DEFAULT_TEASER_FIELDS = {
    "description",
    "preview_image",
    "effective",
    "creators",
}


BUILT_IN_FIELDS = {
    "description": "Description",
    "preview_image": "Preview image",
    "effective": "Publication date",
    "creators": "Creators",
    "subjects": "Tags",
    "language": "Language",
}


def registered_fields():
    """What other add-ons offer on this site, by name. A field refused by
    anyone stays refused."""
    site = api.portal.get()
    result = {}
    for name, provider in getUtilitiesFor(ITeaserFieldProvider):
        try:
            fields = list(provider.fields(site))
        except Exception:
            logger.exception("Teaser field provider %s failed", name)
            continue
        for field in fields:
            existing = result.get(field.name)
            if existing is None or field.never_public:
                result[field.name] = field
    return result


def refused_fields(registered=None):
    registered = registered_fields() if registered is None else registered
    return {name for name, field in registered.items() if field.never_public}


def offered_fields():
    """(name, label) of everything an admin can put in the teaser."""
    registered = registered_fields()
    refused = refused_fields(registered)
    result = dict(BUILT_IN_FIELDS)
    for name, field in registered.items():
        if name not in BUILT_IN_FIELDS:
            result[name] = field.label or name
    return [(name, label) for name, label in result.items() if name not in refused]


def stored_fields():
    try:
        fields = getUtility(IRegistry).get("collective.membersonly.teaser_fields", None)
    except Exception:
        fields = None
    return DEFAULT_TEASER_FIELDS if fields is None else set(fields)


def teaser_fields():
    """The fields in the teaser: what's stored, plus fields that are on by
    default and that no admin has had the chance to turn off yet. The stored
    list can't tell those from fields turned off, and whichever add-on is
    installed first, the other finds the same result."""
    registered = registered_fields()
    known = set(api.portal.get_registry_record(KNOWN_RECORD, default=None) or ())
    fields = set(stored_fields()) | {
        name
        for name, field in registered.items()
        if field.default and name not in known
    }
    return fields - refused_fields(registered)


def remember_offered_fields():
    """An admin has now seen every field: what they left off stays off."""
    if api.portal.get_registry_record(KNOWN_RECORD, default=None) is None:
        return
    names = sorted(registered_fields())
    api.portal.set_registry_record(KNOWN_RECORD, names)


def add_registered_fields(result, obj, request, fields):
    registered = registered_fields()
    for name in sorted(fields & set(registered) - set(BUILT_IN_FIELDS) - set(result)):
        field = registered[name]
        try:
            value = (
                field.serialize(obj, request)
                if field.serialize
                else getattr(aq_base(obj), name, None)
            )
        except Exception:
            # Left out: a teaser can go without a field.
            logger.exception("Teaser field %s failed on %r", name, obj)
            continue
        if value not in (None, "", [], (), {}):
            result[name] = json_compatible(value)


def teaser_data(obj, request):
    """Only the public teaser fields of members-only content, and what this
    visitor is told and offered."""
    wf_tool = getToolByName(obj, "portal_workflow")
    state = wf_tool.getInfoFor(obj, "review_state", None)

    fields = teaser_fields()

    result = {
        "@id": obj.absolute_url(),
        "@type": obj.portal_type,
        "review_state": state,
        "is_members_only": state == "members_only",
        "members_only": access_info(obj),
        "title": obj.Title(),
        # What this visitor is told and offered (login, joining...).
        "access_message": access_message(obj, request),
    }

    if "description" in fields:
        result["description"] = obj.Description()

    if "effective" in fields:
        if hasattr(obj, "effective_date") and obj.effective_date:
            result["effective"] = json_compatible(obj.effective_date)

    if "creators" in fields:
        if hasattr(obj, "creators"):
            result["creators"] = obj.creators

    if "subjects" in fields:
        if hasattr(obj, "subject"):
            result["subjects"] = obj.subject

    if "language" in fields:
        if hasattr(obj, "language"):
            result["language"] = obj.language

    if "preview_image" in fields:
        # Inline preview_image
        if hasattr(obj, "preview_image") and obj.preview_image:
            base_url = obj.absolute_url()
            result["preview_image"] = {
                "download": f"{base_url}/@@teaser-image/preview_image/large",
            }

        # Preview image link
        if not result.get("preview_image"):
            try:
                preview_image_link = getattr(obj, "preview_image_link", None)
                if preview_image_link:
                    target = preview_image_link.to_object
                    if target is not None:
                        scales = target.restrictedTraverse("@@images")
                        scale = scales.scale("image", scale="large")
                        if scale:
                            result["preview_image"] = {
                                "download": scale.url,
                                "width": scale.width,
                                "height": scale.height,
                            }
            except Exception:
                pass

        # Lead image (News Item)
        if not result.get("preview_image"):
            try:
                if hasattr(obj, "image") and obj.image:
                    base_url = obj.absolute_url()
                    result["preview_image"] = {
                        "download": f"{base_url}/@@teaser-image/image/large",
                    }
            except Exception:
                pass

    add_registered_fields(result, obj, request, fields)
    return result


class TeaserView(Service):
    """Returns only public teaser fields for members-only content."""

    def reply(self):
        return teaser_data(self.context, self.request)


@implementer(IPublishTraverse)
class TeaserImageView(Service):
    """Serves image scales for members-only content without requiring View permission."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.fieldname = "preview_image"
        self.scale_name = "large"
        self._traversal_stack = []

    def publishTraverse(self, request, name):
        self._traversal_stack.append(name)
        if len(self._traversal_stack) == 1:
            self.fieldname = name
        elif len(self._traversal_stack) == 2:
            self.scale_name = name
        return self

    def render(self):
        scaling = ImageScaling(self.context, self.request)
        scale = scaling.scale(self.fieldname, scale=self.scale_name)

        if scale is None:
            self.request.response.setStatus(404)
            return b""

        image_data = scale.data
        self.request.response.setStatus(200)
        self.request.response.setHeader("Content-Type", image_data.contentType)

        raw = image_data.data
        if not isinstance(raw, bytes):
            raw = bytes(raw)

        self.request.response.setHeader("Content-Length", len(raw))
        return raw
