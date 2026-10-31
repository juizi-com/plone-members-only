"""Upgrade steps."""

from plone import api


def to_1001(context):
    """Members-only content is read by the "Can view subscription content"
    role instead of every logged-in user. Existing sites keep their
    behaviour: the site root is shared with Logged-in users in that
    column, which the "any logged-in user" setting reflects."""
    from collective.membersonly.access import apply_logged_in_setting
    from collective.membersonly.setuphandlers import build_workflow

    portal = api.portal.get()
    setup = api.portal.get_tool("portal_setup")
    profile = "profile-collective.membersonly:default"
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "plone.app.registry")
    build_workflow(portal, replace=True)
    api.portal.get_tool("portal_workflow").updateRoleMappings()
    api.portal.set_registry_record("collective.membersonly.any_logged_in_user", True)
    apply_logged_in_setting(True, portal)


def to_1002(context):
    """Teaser fields other add-ons can offer, and access information in
    listings. Admins' choices of teaser fields stay as they are."""
    from collective.membersonly.controlpanels.controlpanel import IMembersOnlySettings
    from collective.membersonly.controlpanels.controlpanel import ITeaserState
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility

    registry = getUtility(IRegistry)
    # Not the registry import: that would add the defaults back to the list.
    registry.registerInterface(IMembersOnlySettings, prefix="collective.membersonly")
    registry.registerInterface(
        ITeaserState, prefix="collective.membersonly.teaser_state"
    )
    setup = api.portal.get_tool("portal_setup")
    setup.runImportStepFromProfile(
        "profile-collective.membersonly:default", "catalog", run_dependencies=False
    )
    catalog = api.portal.get_tool("portal_catalog")
    for brain in catalog.unrestrictedSearchResults(review_state="members_only"):
        obj = brain._unrestrictedGetObject()
        catalog.catalog_object(obj, idxs=["review_state"], update_metadata=1)
