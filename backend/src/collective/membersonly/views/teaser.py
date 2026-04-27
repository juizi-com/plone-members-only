from plone.restapi.services import Service
from plone.restapi.serializer.converters import json_compatible
from plone.namedfile.scaling import ImageScaling
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


class TeaserView(Service):
    """Returns only public teaser fields for members-only content."""

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

        # Inline preview_image — point to @@teaser-image instead of @@images
        if hasattr(obj, 'preview_image') and obj.preview_image:
            base_url = obj.absolute_url()
            result['preview_image'] = {
                'download': f'{base_url}/@@teaser-image/preview_image/large',
            }

        # Preview image link (relation to separate image object)
        if not result.get('preview_image'):
            try:
                preview_image_link = getattr(obj, 'preview_image_link', None)
                if preview_image_link:
                    target = preview_image_link.to_object
                    if target is not None:
                        scales = target.restrictedTraverse('@@images')
                        scale = scales.scale('image', scale='large')
                        if scale:
                            result['preview_image'] = {
                                'download': scale.url,
                                'width': scale.width,
                                'height': scale.height,
                            }
            except Exception:
                pass

        # Lead image (News Item)
        if not result.get('preview_image'):
            try:
                if hasattr(obj, 'image') and obj.image:
                    base_url = obj.absolute_url()
                    result['preview_image'] = {
                        'download': f'{base_url}/@@teaser-image/image/large',
                    }
            except Exception:
                pass

        return result


@implementer(IPublishTraverse)
class TeaserImageView(Service):
    """Serves image scales for members-only content without requiring View permission."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.fieldname = 'preview_image'
        self.scale_name = 'large'
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
            return b''

        image_data = scale.data
        self.request.response.setStatus(200)
        self.request.response.setHeader('Content-Type', image_data.contentType)

        # Read raw bytes from the named blob image
        raw = image_data.data
        if not isinstance(raw, bytes):
            raw = bytes(raw)

        self.request.response.setHeader('Content-Length', len(raw))
        return raw
