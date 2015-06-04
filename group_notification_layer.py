from yowsup.layers import YowLayer, YowLayerEvent, YowProtocolLayer
import logging
from protocolentities.notification_groups_added import *
from protocolentities.notification_groups_removed import *
from protocolentities.notification_groups_promoted import *
from protocolentities.iq_groups_participants_promote import *
from protocolentities.iq_groups_participants_promote_success import *
logger = logging.getLogger(__name__)

from os import sys, path

sys.path.append('.')

class YowMyGroupsProtocolLayer(YowProtocolLayer):

    HANDLE = (
        PromoteParticipantsIqProtocolEntity,
    )
    
    def __init__(self):
        handleMap = {
            "iq": (None, self.sendIq),
            "notification": (self.recvNotification, None)
        }
        super(YowMyGroupsProtocolLayer, self).__init__(handleMap)

    def __str__(self):
        return "My Groups Notification Layer"

    def sendIq(self, entity):
        if entity.__class__ in self.__class__.HANDLE:
            if entity.__class__ == PromoteParticipantsIqProtocolEntity:
                self._sendIq(entity, self.onPromoteParticipantsSuccess, self.onPromoteParticipantsFailed)

    def recvNotification(self, node):
        if node["type"] == "w:gp2":
            if node.getChild("add"):
                self.toUpper(AddedGroupNotificationProtocolEntity.fromProtocolTreeNode(node))
            elif node.getChild("promote"):
                self.toUpper(PromotedGroupNotificationProtocolEntity.fromProtocolTreeNode(node))
            elif node.getChild("remove"):
                self.toUpper(RemovedGroupNotificationProtocolEntity.fromProtocolTreeNode(node))

    def onPromoteParticipantsSuccess(self, node, originalIqEntity):
        logger.info("promote participants success")
        self.toUpper(SuccessPromoteParticipantsIqProtocolEntity.fromProtocolTreeNode(node))

    def onPromoteParticipantsFailed(self, node, originalIqEntity):
        logger.error("promote participants failed")
