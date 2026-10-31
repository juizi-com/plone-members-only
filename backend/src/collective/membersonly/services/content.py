"""GET for content, also for people who can't view members-only content:
they get its teaser as a normal page, so Volto shows it with the site's
navigation, breadcrumbs and settings around it."""

from collective.membersonly.access import access_info
from collective.membersonly.access import can_view
from collective.membersonly.access import is_members_only
from collective.membersonly.views.teaser import teaser_data
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.services.content.get import ContentGet
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized


LAYOUT = "members_only_teaser"


class MembersOnlyContentGet(ContentGet):
    def reply(self):
        if can_view(self.context):
            result = super().reply()
            result["members_only"] = access_info(self.context)
            return result
        # The teaser permission is granted far more widely than View (by
        # the site's rolemap, for content in other workflows): anything
        # but members-only content stays as protected as plone.restapi's
        # own GET.
        if not is_members_only(self.context):
            raise Unauthorized("You are not allowed to view this content.")
        # Built here, not by serializing the content: nothing but the
        # teaser fields may reach someone who can't view it.
        result = teaser_data(self.context, self.request)
        info = getToolByName(self.context, "portal_types").getTypeInfo(
            self.context.portal_type
        )
        result.update({
            "type_title": info.Title() if info else self.context.portal_type,
            "layout": LAYOUT,
        })
        # Navigation, breadcrumbs, actions, inherited site settings...
        result.update(expandable_elements(self.context, self.request))
        return result
