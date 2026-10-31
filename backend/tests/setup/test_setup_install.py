from collective.membersonly import PACKAGE_NAME


class TestSetupInstall:
    def test_addon_installed(self, installer):
        """Test if collective.membersonly is installed."""
        assert installer.is_product_installed(PACKAGE_NAME) is True

    def test_browserlayer(self, browser_layers):
        """Test that IBrowserLayer is registered."""
        from collective.membersonly.interfaces import IBrowserLayer

        assert IBrowserLayer in browser_layers

    def test_latest_version(self, profile_last_version):
        """Test latest version of default profile."""
        assert profile_last_version(f"{PACKAGE_NAME}:default") == "1002"


def listed_addons(portal):
    """The add-on ids Site Setup → Add-ons lists (plone.restapi's @addons)."""
    from plone.restapi.services.addons.addons import Addons

    return list(Addons(portal, portal.REQUEST).get_addons())


class TestAddonsListing:
    """Listed in Site Setup → Add-ons only once installed; before that, a
    frontend with volto-collective-formsupport-bulkmailproviders offers the install."""

    def test_listed_once_installed(self, portal, installer):
        assert installer.is_product_installable(PACKAGE_NAME) is True
        assert PACKAGE_NAME in listed_addons(portal)

    def test_hidden_until_installed(self, portal, installer, setup_tool):
        from Products.GenericSetup.tool import UNKNOWN

        setup_tool.setLastVersionForProfile(f"{PACKAGE_NAME}:default", UNKNOWN)

        assert installer.is_product_installed(PACKAGE_NAME) is False
        assert installer.is_product_installable(PACKAGE_NAME) is False
        assert PACKAGE_NAME not in listed_addons(portal)
        # Still installable when asked for explicitly.
        assert installer.is_product_installable(PACKAGE_NAME, allow_hidden=True)

    def test_installs_while_hidden(self, portal, installer, setup_tool):
        """Volto's Install button (POST @addons/<id>/install) still works
        while it's left out of the list: the frontend adds it there."""
        from plone.restapi.services.addons.addons import Addons
        from Products.GenericSetup.tool import UNKNOWN

        setup_tool.setLastVersionForProfile(f"{PACKAGE_NAME}:default", UNKNOWN)

        assert Addons(portal, portal.REQUEST).install_product(PACKAGE_NAME)
        assert installer.is_product_installed(PACKAGE_NAME) is True
        assert PACKAGE_NAME in listed_addons(portal)
