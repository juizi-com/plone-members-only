from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.supermodel import model
from zope import schema
from zope.interface import Interface


class IMembersOnlySettings(model.Schema):
    """Settings for the Members Only addon."""

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