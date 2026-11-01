"""A gated item is in visitors' listings, so its summary has to come from the
catalog alone. A field with no column makes Plone wake the item, and waking a
gated item as a visitor fails the whole listing."""

from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from plone.restapi.testing import RelativeSession
from zope.component import getGlobalSiteManager
from zope.interface import implementer

import pytest
import transaction


@implementer(IJSONSummarySerializerMetadata)
class NoColumnOnThisSite:
    """As plonegovbr.socialmedia on a site where it isn't installed: the
    package is loaded for the whole process, the column is per site."""

    def default_metadata_fields(self):
        return {"no_such_column"}


@pytest.fixture
def listing(functional):
    portal = functional["portal"]
    api.portal.get_tool("portal_workflow").setChainForPortalTypes(
        ["Document"], ["members_only_workflow"]
    )
    setRoles(portal, TEST_USER_ID, ["Manager"])
    gated = api.content.create(
        container=portal, type="Document", id="gated", title="Gated"
    )
    api.content.transition(obj=gated, transition="restrict_to_members")
    transaction.commit()
    gsm = getGlobalSiteManager()
    utility = NoColumnOnThisSite()
    gsm.registerUtility(utility, IJSONSummarySerializerMetadata, name="no-column")
    session = RelativeSession(portal.absolute_url())
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()
    gsm.unregisterUtility(utility, IJSONSummarySerializerMetadata, name="no-column")


def test_field_without_a_column_keeps_the_listing(listing):
    response = listing.get("/@search", params={"portal_type": "Document"})
    assert response.status_code == 200
    item = next(i for i in response.json()["items"] if i["title"] == "Gated")
    assert "no_such_column" not in item


def test_fields_that_never_needed_a_column_stay(listing):
    item = listing.get("/@search", params={"portal_type": "Document"}).json()["items"][0]
    assert item["@type"] == "Document"
    assert item["type_title"]
    assert item["review_state"] == "members_only"
