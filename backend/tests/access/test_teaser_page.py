"""Members-only content someone can't read comes from GET as a teaser page
(not a 401), with @components so Volto's header works around it; nothing
else is any easier to read."""

from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession

import pytest
import transaction


MEMBERS_TEXT = "Only members may read this."


@pytest.fixture
def site(functional):
    portal = functional["portal"]
    wf = api.portal.get_tool("portal_workflow")
    wf.setChainForPortalTypes(["Document"], ["members_only_workflow"])
    wf.setChainForPortalTypes(["News Item"], ["simple_publication_workflow"])
    setRoles(portal, TEST_USER_ID, ["Manager"])
    folder = api.content.create(
        container=portal, type="Document", id="library", title="Library"
    )
    api.content.transition(obj=folder, transition="publish")
    page = api.content.create(
        container=folder,
        type="Document",
        id="paper",
        title="Paper",
        description="A teaser for the paper.",
        blocks={"b1": {"@type": "slate", "plaintext": MEMBERS_TEXT}},
        blocks_layout={"items": ["b1"]},
    )
    api.content.transition(obj=page, transition="restrict_to_members")
    api.content.create(container=folder, type="Document", id="draft", title="Draft")
    api.content.create(container=portal, type="News Item", id="news", title="News")
    api.user.create(email="m@example.com", username="member", password="secret-pass-1")  # noqa: S106
    transaction.commit()
    return portal


def session(portal, auth=None):
    s = RelativeSession(portal.absolute_url(), test=None)
    s.headers.update({"Accept": "application/json"})
    if auth:
        s.auth = auth
    return s


class TestTeaserPage:
    def test_anonymous_gets_the_teaser(self, site):
        response = session(site).get("/library/paper?expand=navigation,breadcrumbs")
        assert response.status_code == 200
        data = response.json()
        assert data["layout"] == "members_only_teaser"
        assert data["is_members_only"] is True
        assert data["title"] == "Paper"
        assert data["description"] == "A teaser for the paper."
        assert data["access_message"]["text"]
        # The page around it: navigation, breadcrumbs, actions...
        assert data["@components"]["navigation"]["items"]
        assert [b["title"] for b in data["@components"]["breadcrumbs"]["items"]] == [
            "Library",
            "Paper",
        ]
        assert "actions" in data["@components"]

    def test_the_teaser_holds_nothing_else(self, site):
        response = session(site).get("/library/paper")
        assert MEMBERS_TEXT not in response.text
        assert not {"blocks", "blocks_layout", "text", "UID", "items"} & set(
            response.json()
        )

    def test_someone_who_can_view_gets_the_content(self, site):
        response = session(site, ("member", "secret-pass-1")).get("/library/paper")
        assert response.status_code == 200
        data = response.json()
        assert data["layout"] != "members_only_teaser"
        assert "blocks" in data
        assert MEMBERS_TEXT in response.text

    def test_private_members_only_workflow_content_stays_closed(self, site):
        assert session(site).get("/library/draft").status_code == 401

    def test_private_content_in_other_workflows_stays_closed(self, site):
        # The teaser permission is granted site-wide outside the
        # members-only workflow: GET must still need View there.
        assert session(site).get("/news").status_code == 401

    def test_managers_still_get_everything(self, site):
        response = session(site, (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)).get(
            "/library/draft"
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Draft"
