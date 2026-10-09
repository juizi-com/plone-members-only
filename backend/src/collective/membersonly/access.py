"""Who may read members-only content, and what others are told."""

from collective.membersonly.interfaces import IAccessMessage
from collective.membersonly.roles import ROLE
from plone import api
from zope.component import queryUtility


LOGGED_IN = "AuthenticatedUsers"
SETTING = "collective.membersonly.any_logged_in_user"


def any_logged_in_user_enabled(portal=None):
    portal = portal or api.portal.get()
    return ROLE in portal.get_local_roles_for_userid(LOGGED_IN)


def apply_logged_in_setting(enabled, portal=None):
    """Share the site root with "Logged-in users" in the "Can view
    subscription content" column (or stop): the add-on's original
    behaviour, where any logged-in user reads members-only content."""
    portal = portal or api.portal.get()
    roles = set(portal.get_local_roles_for_userid(LOGGED_IN))
    if enabled:
        roles.add(ROLE)
    else:
        roles.discard(ROLE)
    if roles:
        portal.manage_setLocalRoles(LOGGED_IN, sorted(roles))
    else:
        portal.manage_delLocalRoles([LOGGED_IN])
    portal.reindexObjectSecurity()


def setting_changed(settings, event):
    if event.record.fieldName == "any_logged_in_user":
        apply_logged_in_setting(bool(event.newValue))


def default_message(context, request):
    login = f"{context.absolute_url()}/login"
    if api.user.is_anonymous():
        return {
            "text": "This content is available to members only.",
            "actions": [{"label": "Log in to read", "url": login}],
        }
    return {"text": "You don't have access to this content.", "actions": []}


def access_message(context, request):
    provider = queryUtility(IAccessMessage)
    if provider is not None:
        try:
            message = provider(context, request)
            if message:
                return message
        except Exception:
            import logging

            logging.getLogger("collective.membersonly").exception(
                "The access message provider failed; using the default"
            )
    return default_message(context, request)
