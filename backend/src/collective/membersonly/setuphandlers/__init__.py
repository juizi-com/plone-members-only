from plone.base.interfaces.installable import INonInstallable
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.exportimport import _initDCWorkflow
from Products.DCWorkflow.exportimport import WorkflowDefinitionConfigurator
from zope.component.hooks import getSite
from zope.interface import implementer

import logging
import os


logger = logging.getLogger("collective.membersonly")


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "collective.membersonly:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return [
            "collective.membersonly.upgrades",
        ]


def post_install(context):
    """Creates the members_only_workflow, and applies the "any logged-in
    user" setting (on for a new install: the original behaviour)."""
    portal = getSite()
    build_workflow(portal)
    from collective.membersonly.access import apply_logged_in_setting
    from plone import api

    apply_logged_in_setting(
        bool(
            api.portal.get_registry_record(
                "collective.membersonly.any_logged_in_user", default=True
            )
        ),
        portal,
    )


def build_workflow(portal, replace=False):
    """The workflow from definition.xml. replace=True rebuilds an existing
    one (an upgrade changed the definition); content keeps its state,
    which is stored on the content under the workflow's id."""
    wf_tool = getToolByName(portal, "portal_workflow")

    if "members_only_workflow" in list(wf_tool.objectIds()):
        if not replace:
            return
        wf_tool._delObject("members_only_workflow")

    wf = DCWorkflowDefinition("members_only_workflow")
    wf_tool._setObject("members_only_workflow", wf)
    wf_ob = wf_tool._getOb("members_only_workflow")

    definition_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "profiles",
        "default",
        "workflows",
        "members_only_workflow",
        "definition.xml",
    )

    with open(definition_path, "rb") as f:
        body = f.read()

    configurator = WorkflowDefinitionConfigurator(wf_ob)
    info = configurator.parseWorkflowXML(body)

    _initDCWorkflow(
        wf_ob,
        info[1],  # title
        info[11],  # description
        info[12],  # manager_bypass
        info[13],  # creation_guard
        info[2],  # state_variable
        info[3],  # initial_state
        info[4],  # states
        info[5],  # transitions
        info[6],  # variables
        info[7],  # worklists
        info[8],  # permissions
        info[9],  # groups
        info[10],  # scripts
        None,  # context
    )


def uninstall(context):
    """Uninstall handler — retracts members_only content to private with audit note,
    then removes the workflow and cleans up registry records."""
    from DateTime import DateTime
    from datetime import datetime

    portal = getSite()
    wf_tool = getToolByName(portal, "portal_workflow")
    catalog = getToolByName(portal, "portal_catalog")

    # Determine fallback workflow
    fallback_workflow = "simple_publication_workflow"

    # Find all content in members_only state before removing workflow
    brains = catalog.searchResults(review_state="members_only")
    retracted_paths = []

    comment = (
        f'This item was in "Members only" state when the '
        f"collective.membersonly addon was uninstalled on "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}. "
        f"It has been retracted to Private. Please review and "
        f"republish as appropriate."
    )

    for brain in brains:
        try:
            obj = brain.getObject()
            wf_tool.doActionFor(obj, "retract", comment=comment)
            obj.reindexObject(idxs=["review_state"])
            retracted_paths.append(brain.getPath())
        except Exception as e:
            logger.warning(f"Could not retract {brain.getPath()}: {e}")

    if retracted_paths:
        logger.info(
            f"collective.membersonly uninstall: retracted {len(retracted_paths)} "
            f"items to private: {', '.join(retracted_paths)}"
        )

    # Remove the workflow
    if "members_only_workflow" in list(wf_tool.objectIds()):
        wf_tool._delObject("members_only_workflow")

    # Reset default chain if it was members_only_workflow
    if "members_only_workflow" in wf_tool._default_chain:
        wf_tool.setDefaultChain(fallback_workflow)
        logger.info(
            f"collective.membersonly uninstall: reset default workflow "
            f"chain to {fallback_workflow}"
        )

    # Remove members_only_workflow from any explicit type bindings
    chains = dict(wf_tool._chains_by_type)
    for pt, wfs in chains.items():
        if "members_only_workflow" in wfs:
            new_wfs = tuple(w for w in wfs if w != "members_only_workflow")
            wf_tool.setChainForPortalTypes([pt], list(new_wfs) or [fallback_workflow])

    # Fix workflow history on any remaining orphaned items
    all_brains = catalog.searchResults(portal_type=["Document", "News Item", "Folder"])
    for brain in all_brains:
        try:
            obj = brain.getObject()
            history = obj.workflow_history
            if "members_only_workflow" in history and fallback_workflow not in history:
                history[fallback_workflow] = (
                    {
                        "action": None,
                        "review_state": "private",
                        "comments": comment,
                        "actor": "admin",
                        "time": DateTime(),
                    },
                )
                obj.reindexObject(idxs=["review_state"])
                logger.info(f"Fixed orphaned workflow history on {brain.getPath()}")
        except Exception as e:
            logger.warning(f"Could not fix workflow history on {brain.getPath()}: {e}")

    # Remove registry records
    try:
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility

        registry = getUtility(IRegistry)
        keys_to_remove = [
            key
            for key in registry.records.keys()
            if key.startswith("collective.membersonly")
        ]
        for key in keys_to_remove:
            del registry.records[key]
    except Exception as e:
        logger.warning(f"Could not clean registry: {e}")
