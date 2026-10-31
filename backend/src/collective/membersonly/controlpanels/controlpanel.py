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
            'people and groups given "Can view subscription content" on the '
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
        value_type=schema.Choice(vocabulary="collective.membersonly.teaser_fields"),
        default=[
            "description",
            "preview_image",
            "effective",
            "creators",
        ],
        required=False,
    )


class ITeaserState(model.Schema):
    """Bookkeeping, not a setting: not in the panel."""

    known = schema.List(
        title="Teaser fields an admin has seen",
        value_type=schema.TextLine(),
        default=[],
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


from collective.membersonly.views.teaser import remember_offered_fields  # noqa: E402
from collective.membersonly.views.teaser import teaser_fields  # noqa: E402
from plone.restapi.deserializer import json_body  # noqa: E402
from plone.restapi.deserializer.controlpanels import (  # noqa: E402
    ControlpanelDeserializeFromJson,
)
from plone.restapi.interfaces import IDeserializeFromJson  # noqa: E402
from plone.restapi.interfaces import ISerializeToJson  # noqa: E402
from plone.restapi.serializer.controlpanels import (  # noqa: E402
    ControlpanelSerializeToJson,
)
from zope.interface import implementer  # noqa: E402
from zope.schema.interfaces import IVocabularyFactory  # noqa: E402
from zope.component import getUtility  # noqa: E402


@implementer(ISerializeToJson)
@adapter(MembersOnlyConfigletPanel)
class MembersOnlyPanelToJson(ControlpanelSerializeToJson):
    """The panel shows what the teaser really has, which can be more than
    what's stored: see teaser_fields."""

    def __call__(self):
        result = super().__call__()
        chosen = teaser_fields()
        terms = getUtility(
            IVocabularyFactory, name="collective.membersonly.teaser_fields"
        )(self.controlpanel.context)
        result["data"]["teaser_fields"] = [
            {"token": term.token, "title": term.title}
            for term in terms
            if term.value in chosen
        ]
        return result


@implementer(IDeserializeFromJson)
@adapter(MembersOnlyConfigletPanel)
class MembersOnlyPanelFromJson(ControlpanelDeserializeFromJson):
    def __call__(self, mask_validation_errors=True):
        super().__call__(mask_validation_errors)
        if "teaser_fields" in json_body(self.controlpanel.request):
            remember_offered_fields()
