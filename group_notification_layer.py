from yowsup.layers import YowLayer, YowLayerEvent, YowProtocolLayer
import logging
from protocolentities.notification_groups_promoted import *
logger = logging.getLogger(__name__)

from os import sys, path

sys.path.append('.')

class YowMyGroupsProtocolLayer(YowProtocolLayer):
    
    def __init__(self):
        handleMap = {
            "notification": (self.recvNotification, None)
        }
        super(YowMyGroupsProtocolLayer, self).__init__(handleMap)

    def __str__(self):
        return "My Groups Notification Layer"

    def recvNotification(self, node):
        if node["type"] == "w:gp2":
            if node.getChild("promote"):
                self.toUpper(PromotedGroupNotificationProtocolEntity.fromProtocolTreeNode(node))

    def onPromoteParticipantsSuccess(self, node, originalIqEntity):
        logger.info("promote participants success")
        self.toUpper(SuccessPromoteParticipantsIqProtocolEntity.fromProtocolTreeNode(node))

    def onPromoteParticipantsFailed(self, node, originalIqEntity):
        logger.error("promote participants failed")
