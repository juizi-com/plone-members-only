from plone.restapi.services import Service
from plone.restapi.serializer.converters import json_compatible
from Products.CMFCore.utils import getToolByName


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

        # Preview image (inline)
        if hasattr(obj, 'preview_image') and obj.preview_image:
            scales = obj.restrictedTraverse('@@images')
            try:
                scale = scales.scale('preview_image', scale='large')
                if scale:
                    result['preview_image'] = {
                        'download': scale.url,
                        'width': scale.width,
                        'height': scale.height,
                    }
            except Exception:
                pass

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
                    scales = obj.restrictedTraverse('@@images')
                    scale = scales.scale('image', scale='large')
                    if scale:
                        result['preview_image'] = {
                            'download': scale.url,
                            'width': scale.width,
                            'height': scale.height,
                        }
            except Exception:
                pass

        return result