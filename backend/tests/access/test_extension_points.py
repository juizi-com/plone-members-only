"""What other add-ons can build on. Nothing here changes the default: every
test without a provider is the add-on on its own."""

from collective.membersonly.interfaces import ITeaserFieldProvider
from collective.membersonly.interfaces import TeaserField
from collective.membersonly.views.teaser import KNOWN_RECORD
from collective.membersonly.views.teaser import teaser_fields
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from zope.component import getGlobalSiteManager
from zope.interface import implementer

import pytest
import transaction


PANEL = "/@controlpanels/members-only"


@pytest.fixture
def site(functional):
    portal = functional["portal"]
    wf = api.portal.get_tool("portal_workflow")
    wf.setChainForPortalTypes(["Document"], ["members_only_workflow"])
    setRoles(portal, TEST_USER_ID, ["Manager"])
    gated = api.content.create(
        container=portal,
        type="Document",
        id="gated",
        title="Gated",
        description="The teaser.",
    )
    api.content.transition(obj=gated, transition="restrict_to_members")
    public = api.content.create(
        container=portal, type="Document", id="public", title="Public"
    )
    api.content.transition(obj=public, transition="publish")
    api.user.create(email="m@example.com", username="member", password="secret-pass-1")  # noqa: S106
    gated.secret = "not for visitors"  # noqa: S105
    gated.summary = "A summary."
    transaction.commit()
    return portal


def session(portal, auth=None):
    s = RelativeSession(portal.absolute_url(), test=None)
    s.headers.update({"Accept": "application/json"})
    if auth:
        s.auth = auth
    return s


def owner(portal):
    return session(portal, (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))


@implementer(ITeaserFieldProvider)
class Provider:
    def __init__(self, fields=None, fail=False):
        self._fields = fields or []
        self.fail = fail

    def fields(self, site):
        if self.fail:
            raise ValueError("broken")
        return self._fields


@pytest.fixture
def provide():
    gsm = getGlobalSiteManager()
    registered = []

    def register(*fields, fail=False, name="test"):
        provider = Provider(fields, fail)
        gsm.registerUtility(provider, ITeaserFieldProvider, name=name)
        registered.append((provider, name))
        transaction.commit()
        return provider

    yield register
    for provider, name in registered:
        gsm.unregisterUtility(provider, ITeaserFieldProvider, name=name)


def tokens(panel):
    return {item["token"] for item in panel["data"]["teaser_fields"]}


class TestAccessInformation:
    def test_anonymous_on_gated(self, site):
        body = session(site).get("/gated").json()
        assert body["members_only"] == {"gated": True, "can_view": False}

    def test_teaser_endpoint(self, site):
        body = session(site).get("/gated/@@teaser").json()
        assert body["members_only"] == {"gated": True, "can_view": False}

    def test_someone_with_access(self, site):
        body = session(site, ("member", "secret-pass-1")).get("/gated").json()
        assert body["members_only"] == {"gated": True, "can_view": True}

    def test_public_content(self, site):
        body = session(site).get("/public").json()
        assert body["members_only"] == {"gated": False, "can_view": True}

    def test_listings_say_what_is_gated(self, site):
        items = session(site).get("/@search?portal_type=Document").json()["items"]
        assert {i["@id"].split("/")[-1]: i["members_only"] for i in items} == {
            "gated": True,
            "public": False,
        }

    def test_the_flag_follows_the_state(self, site):
        api.content.transition(obj=site["public"], transition="retract_to_members")
        transaction.commit()
        items = session(site).get("/@search?id=public").json()["items"]
        assert items[0]["members_only"] is True

    def test_gated_items_reach_the_sitemap(self, site):
        """Volto builds its sitemap from anonymous @search."""
        items = session(site).get("/@search?metadata_fields=modified").json()["items"]
        assert any(i["@id"].endswith("/gated") for i in items)


class TestWithoutProviders:
    def test_defaults_are_unchanged(self, site):
        assert teaser_fields() == {
            "description",
            "preview_image",
            "effective",
            "creators",
        }

    def test_panel_lists_the_built_in_fields(self, site):
        panel = owner(site).get(PANEL).json()
        assert tokens(panel) == {
            "description",
            "preview_image",
            "effective",
            "creators",
        }

    def test_panel_still_saves(self, site):
        s = owner(site)
        r = s.patch(PANEL, json={"teaser_fields": ["description", "language"]})
        assert r.status_code == 204
        assert tokens(s.get(PANEL).json()) == {"description", "language"}


class TestProvidedFields:
    def test_field_that_is_on_by_default(self, site, provide):
        provide(TeaserField("summary", "Summary", default=True))
        assert session(site).get("/gated").json()["summary"] == "A summary."

    def test_field_that_is_off_by_default(self, site, provide):
        provide(TeaserField("summary", "Summary"))
        assert "summary" not in session(site).get("/gated").json()

    def test_the_panel_shows_what_the_teaser_has(self, site, provide):
        provide(TeaserField("summary", "Summary", default=True))
        assert "summary" in tokens(owner(site).get(PANEL).json())

    def test_turned_on_by_an_admin(self, site, provide):
        provide(TeaserField("summary", "Summary"))
        owner(site).patch(PANEL, json={"teaser_fields": ["description", "summary"]})
        assert session(site).get("/gated").json()["summary"] == "A summary."

    def test_turned_off_by_an_admin_stays_off(self, site, provide):
        """The list is what it was: only the bookkeeping tells them apart."""
        provide(TeaserField("summary", "Summary", default=True))
        owner(site).patch(
            PANEL,
            json={
                "teaser_fields": [
                    "description",
                    "preview_image",
                    "effective",
                    "creators",
                ]
            },
        )
        transaction.begin()
        assert "summary" in api.portal.get_registry_record(KNOWN_RECORD)
        assert "summary" not in session(site).get("/gated").json()

    def test_a_field_added_later_is_still_on_by_default(self, site, provide):
        provide(TeaserField("summary", "Summary", default=True))
        owner(site).patch(PANEL, json={"teaser_fields": ["description"]})
        provide(TeaserField("secret", "Later", default=True), name="later")
        assert session(site).get("/gated").json()["secret"] == "not for visitors"  # noqa: S105

    def test_serialize(self, site, provide):
        provide(
            TeaserField(
                "shouted",
                "Shouted",
                default=True,
                serialize=lambda obj, request: obj.title.upper(),
            )
        )
        assert session(site).get("/gated").json()["shouted"] == "GATED"

    def test_empty_value_is_left_out(self, site, provide):
        provide(TeaserField("nothing_here", "Nothing", default=True))
        assert "nothing_here" not in session(site).get("/gated").json()

    def test_a_failing_field_loses_only_itself(self, site, provide):
        def fail(obj, request):
            raise ValueError("broken")

        provide(
            TeaserField("broken", "Broken", default=True, serialize=fail),
            TeaserField("summary", "Summary", default=True),
        )
        body = session(site).get("/gated").json()
        assert "broken" not in body
        assert body["summary"] == "A summary."

    def test_a_failing_provider_loses_only_itself(self, site, provide):
        provide(fail=True)
        assert session(site).get("/gated").json()["title"] == "Gated"

    def test_a_field_cant_replace_the_teaser(self, site, provide):
        provide(
            TeaserField(
                "access_message",
                "Hijack",
                default=True,
                serialize=lambda obj, request: "hijacked",
            ),
            TeaserField(
                "title",
                "Hijack",
                default=True,
                serialize=lambda obj, request: "hijacked",
            ),
        )
        body = session(site).get("/gated").json()
        assert body["title"] == "Gated"
        assert body["access_message"] != "hijacked"

    def test_not_for_people_with_access_only(self, site, provide):
        """It's a teaser field: someone with access gets the normal page."""
        provide(TeaserField("summary", "Summary", default=True))
        body = session(site, ("member", "secret-pass-1")).get("/gated").json()
        assert "summary" not in body


class TestRefusedFields:
    def test_refused_even_if_stored(self, site, provide):
        provide(TeaserField("secret", never_public=True))
        api.portal.set_registry_record(
            "collective.membersonly.teaser_fields", ["description"]
        )
        record = site.portal_registry.records["collective.membersonly.teaser_fields"]
        record._value = ["description", "secret"]
        transaction.commit()
        assert "secret" not in session(site).get("/gated").json()

    def test_refused_even_if_offered_elsewhere(self, site, provide):
        provide(TeaserField("secret", "Secret", default=True), name="one")
        provide(TeaserField("secret", never_public=True), name="two")
        assert "secret" not in session(site).get("/gated").json()

    def test_refused_even_if_default_on(self, site, provide):
        provide(TeaserField("secret", default=True, never_public=True))
        assert "secret" not in session(site).get("/gated").json()

    def test_a_built_in_field_can_be_refused(self, site, provide):
        provide(TeaserField("description", never_public=True))
        assert "description" not in session(site).get("/gated").json()

    def test_not_in_the_panel(self, site, provide):
        provide(TeaserField("secret", "Secret", never_public=True))
        body = owner(site).get("/@vocabularies/collective.membersonly.teaser_fields")
        assert "secret" not in {item["token"] for item in body.json()["items"]}

    def test_cant_be_saved(self, site, provide):
        provide(TeaserField("secret", "Secret", never_public=True))
        r = owner(site).patch(PANEL, json={"teaser_fields": ["secret"]})
        assert r.status_code == 400


class TestUpgrade:
    def test_keeps_an_admins_choice_and_fills_listings(self, site):
        from collective.membersonly.upgrades import to_1002

        name = "collective.membersonly.teaser_fields"
        api.portal.set_registry_record(name, ["language"])
        catalog = api.portal.get_tool("portal_catalog")
        catalog.delColumn("members_only")
        to_1002(None)
        transaction.commit()
        assert api.portal.get_registry_record(name) == ["language"]
        assert teaser_fields() == {"language"}
        items = session(site).get("/@search?id=gated").json()["items"]
        assert items[0]["members_only"] is True
