from plone.base.interfaces.installable import INonInstallable
from zope.interface import implementer
from zope.component.hooks import getSite
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.exportimport import WorkflowDefinitionConfigurator
from Products.DCWorkflow.exportimport import _initDCWorkflow
from Products.CMFCore.utils import getToolByName
import os


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
    """Post install script - creates the members_only_workflow."""
    portal = getSite()
    wf_tool = getToolByName(portal, 'portal_workflow')

    if 'members_only_workflow' in list(wf_tool.objectIds()):
        return

    wf = DCWorkflowDefinition('members_only_workflow')
    wf_tool._setObject('members_only_workflow', wf)
    wf_ob = wf_tool._getOb('members_only_workflow')

    definition_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'profiles',
        'default',
        'workflows',
        'members_only_workflow',
        'definition.xml'
    )

    with open(definition_path, 'rb') as f:
        body = f.read()

    configurator = WorkflowDefinitionConfigurator(wf_ob)
    info = configurator.parseWorkflowXML(body)

    _initDCWorkflow(
        wf_ob,
        info[1],   # title
        info[11],  # description
        info[12],  # manager_bypass
        info[13],  # creation_guard
        info[2],   # state_variable
        info[3],   # initial_state
        info[4],   # states
        info[5],   # transitions
        info[6],   # variables
        info[7],   # worklists
        info[8],   # permissions
        info[9],   # groups
        info[10],  # scripts
        None       # context
    )