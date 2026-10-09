from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.supermodel import model
from zope import schema


class IMembersOnlySettings(model.Schema):
    """Settings for the Members Only addon."""

    any_logged_in_user = schema.Bool(
        title="Any logged-in user can view members-only content",
        description=(
            "On: everyone with an account reads members-only content (the "
            "Sharing tab shows the site shared with Logged-in users). Off: only "
            "people and groups given \"Can view subscription content\" on the "
            "Sharing tab, for example by a membership add-on."
        ),
        default=True,
        required=False,
    )

    teaser_fields = schema.List(
        title="Teaser fields",
        description=(
            "Fields to include in the public teaser for members-only content. "
            "All sites get title and review_state regardless of this setting."
        ),
        value_type=schema.Choice(
            values=[
                'description',
                'preview_image',
                'effective',
                'creators',
                'subjects',
                'language',
            ]
        ),
        default=[
            'description',
            'preview_image',
            'effective',
            'creators',
        ],
        required=False,
    )


class MembersOnlyControlPanelForm(RegistryEditForm):
    schema = IMembersOnlySettings
    schema_prefix = "collective.membersonly"
    label = "Members Only Settings"
    description = "Configure which fields are surfaced in the public teaser for members-only content."


class MembersOnlyControlPanelView(ControlPanelFormWrapper):
    form = MembersOnlyControlPanelForm

from plone.restapi.controlpanels import RegistryConfigletPanel  # noqa: E402
from zope.component import adapter  # noqa: E402
from zope.interface import Interface as _Interface  # noqa: E402


@adapter(_Interface, _Interface)
class MembersOnlyConfigletPanel(RegistryConfigletPanel):
    """The same settings in Volto's Site Setup."""
    schema = IMembersOnlySettings
    schema_prefix = "collective.membersonly"
    configlet_id = "collective.membersonly"
    configlet_category_id = "Products"
    title = "Members Only"
    group = "Products"
