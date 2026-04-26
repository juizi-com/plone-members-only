from plone.restapi.services import Service
from plone.restapi.serializer.converters import json_compatible
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class TeaserView(Service):
    """Returns only public teaser fields for members-only content."""

    TEASER_FIELDS = {
        'title',
        'description',
        'effective',
        'creators',
    }

    def reply(self):
        obj = self.context
        wf_tool = getToolByName(obj, 'portal_workflow')
        state = wf_tool.getInfoFor(obj, 'review_state', None)

        result = {
            '@id': obj.absolute_url(),
            '@type': obj.portal_type,
            'review_state': state,
            'is_members_only': state == 'members_only',
            'title': obj.Title(),
            'description': obj.Description(),
        }

        if hasattr(obj, 'effective_date') and obj.effective_date:
            result['effective'] = json_compatible(obj.effective_date)

        if hasattr(obj, 'creators'):
            result['creators'] = obj.creators

        # Preview image
        if hasattr(obj, 'preview_image') and obj.preview_image:
            scales = obj.restrictedTraverse('@@images')
            try:
                scale = scales.scale('preview_image', scale='preview')
                if scale:
                    result['preview_image'] = {
                        'download': scale.url,
                        'width': scale.width,
                        'height': scale.height,
                    }
            except Exception:
                pass

        return result