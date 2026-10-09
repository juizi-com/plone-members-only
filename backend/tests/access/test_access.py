"""Who reads members-only content: the "Can view subscription content"
Sharing role, the any-logged-in-user setting, and the access message."""
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from zope.component import getGlobalSiteManager
from zope.interface import implementer

from collective.membersonly import access
from collective.membersonly.interfaces import IAccessMessage

import pytest


@pytest.fixture
def page(portal):
    wf = api.portal.get_tool('portal_workflow')
    wf.setChainForPortalTypes(['Document'], ['members_only_workflow'])
    setRoles(portal, TEST_USER_ID, ['Manager'])
    folder = api.content.create(container=portal, type='Document', id='library', title='Library')
    page = api.content.create(container=folder, type='Document', id='paper', title='Paper')
    api.content.transition(obj=page, transition='restrict_to_members')
    api.content.create(container=folder, type='Document', id='draft', title='Draft')
    api.user.create(email='m@example.com', username='member', password='secret-pass-1')  # noqa: S106
    api.group.create(groupname='research')
    setRoles(portal, TEST_USER_ID, ['Member'])
    return page


def can_view(username, obj):
    # borg.localrole caches local roles per request; in real use each
    # change and each check are separate requests.
    from zope.annotation.interfaces import IAnnotations
    from zope.globalrequest import getRequest
    IAnnotations(getRequest()).clear()
    with api.env.adopt_user(username=username):
        return api.user.has_permission('View', obj=obj)


class TestSetting:

    def test_new_install_keeps_any_logged_in_user(self, portal, page):
        assert api.portal.get_registry_record('collective.membersonly.any_logged_in_user')
        assert access.any_logged_in_user_enabled(portal)
        assert can_view('member', page)

    def test_switching_it_off(self, portal, page):
        api.portal.set_registry_record('collective.membersonly.any_logged_in_user', False)
        assert not access.any_logged_in_user_enabled(portal)
        assert not can_view('member', page)
        api.portal.set_registry_record('collective.membersonly.any_logged_in_user', True)
        assert can_view('member', page)

    def test_upgrade_keeps_existing_behaviour(self, portal, page):
        from collective.membersonly.upgrades import to_1001
        api.portal.set_registry_record('collective.membersonly.any_logged_in_user', False)
        setRoles(portal, TEST_USER_ID, ['Manager'])
        to_1001(api.portal.get_tool('portal_setup'))
        assert access.any_logged_in_user_enabled(portal)
        assert api.content.get_state(page) == 'members_only'
        assert can_view('member', page)


class TestSharingRole:

    @pytest.fixture(autouse=True)
    def only_shared(self, portal, page):
        api.portal.set_registry_record('collective.membersonly.any_logged_in_user', False)

    def test_role_on_the_sharing_tab(self, portal, page, http_request):
        setRoles(portal, TEST_USER_ID, ['Manager'])
        view = api.content.get_view('sharing', page, http_request)
        assert 'Can view subscription content' in [r['title'] for r in view.roles()]

    def test_shared_with_a_person(self, page):
        api.user.grant_roles(username='member', obj=page, roles=['Subscriber'])
        assert can_view('member', page)

    def test_shared_folder_with_a_group(self, page):
        api.group.add_user(groupname='research', username='member')
        api.group.grant_roles(groupname='research', obj=page.aq_parent, roles=['Subscriber'])
        assert can_view('member', page)

    def test_private_items_stay_hidden(self, page):
        api.group.add_user(groupname='research', username='member')
        api.group.grant_roles(groupname='research', obj=page.aq_parent, roles=['Subscriber'])
        assert not can_view('member', page.aq_parent['draft'])

    def test_anonymous_never(self, page):
        api.user.grant_roles(username='member', obj=page, roles=['Subscriber'])
        logout()
        assert not api.user.has_permission('View', obj=page)


class TestAccessMessage:

    def test_defaults(self, portal, page, http_request):
        logout()
        message = access.access_message(page, http_request)
        assert message['actions'][0]['label'] == 'Log in to read'
        login(portal, TEST_USER_NAME)
        assert access.access_message(page, http_request)['actions'] == []

    def test_provider_and_fallback(self, page, http_request):
        @implementer(IAccessMessage)
        class Custom:
            def __call__(self, context, request):
                return {'text': 'Join us', 'actions': []}

        @implementer(IAccessMessage)
        class Broken:
            def __call__(self, context, request):
                raise ValueError('boom')

        gsm = getGlobalSiteManager()
        custom = Custom()
        gsm.registerUtility(custom, IAccessMessage)
        try:
            assert access.access_message(page, http_request)['text'] == 'Join us'
        finally:
            gsm.unregisterUtility(custom, IAccessMessage)
        broken = Broken()
        gsm.registerUtility(broken, IAccessMessage)
        try:
            assert access.access_message(page, http_request)['text'].startswith('You don')
        finally:
            gsm.unregisterUtility(broken, IAccessMessage)

    def test_teaser_carries_the_message(self, portal, page, http_request):
        logout()
        view = api.content.get_view('teaser', page, http_request)
        assert view.reply()['access_message']['actions'][0]['label'] == 'Log in to read'

