"""The "Can view subscription content" column on the Sharing tab.

Content in the members-only state is readable by people (or groups) given
this role on it or on a folder above it. In the private and pending
states the role grants nothing, so unpublished items in a shared folder
stay hidden.
"""
from plone.app.workflow.interfaces import ISharingPageRole
from zope.interface import implementer

ROLE = 'Subscriber'


@implementer(ISharingPageRole)
class SubscriberRole:
    title = 'Can view subscription content'
    required_permission = 'collective.membersonly.DelegateSubscriber'
    required_interface = None
