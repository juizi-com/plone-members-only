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
    setup = api.portal.get_tool('portal_setup')
    profile = 'profile-collective.membersonly:default'
    setup.runImportStepFromProfile(profile, 'rolemap')
    setup.runImportStepFromProfile(profile, 'plone.app.registry')
    build_workflow(portal, replace=True)
    api.portal.get_tool('portal_workflow').updateRoleMappings()
    api.portal.set_registry_record('collective.membersonly.any_logged_in_user', True)
    apply_logged_in_setting(True, portal)
