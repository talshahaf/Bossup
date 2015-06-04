from yowsup.structs import ProtocolEntity, ProtocolTreeNode
from yowsup.layers.protocol_notifications.protocolentities import NotificationProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.notification_groups import GroupsNotificationProtocolEntity

class PromotedGroupNotificationProtocolEntity(GroupsNotificationProtocolEntity):
    '''

    <notification notify="WhatsApp" id="{{id}}" t="{{TIMESTAMP}}" participant="{{PARTICIPANT_JID}}" from="{{GROUP_JID}}" type="w:gp2">
        <promote>
            <participant type="admin" jid="{{JID_1}}">\n</participant>
            <participant jid="{{JID_2}}">\n</participant>
        </promote>
    </notification>

    '''

    def __init__(self, _type, _id,  _from, timestamp, notify, participant, participants):
        super(PromotedGroupNotificationProtocolEntity, self).__init__(_id, _from, timestamp, notify, participant)
        self.setParticipantsData(participants)

    def setParticipantsData(self, participants):
        self.participants = participants

    def getParticipants(self):
        return self.participants
        
    def getPromoter(self, full = True):
        return self.participant if full else self.participant.split('@')[0]

    def __str__(self):
        out = super(PromotedGroupNotificationProtocolEntity, self).__str__()
        out += "participants: %s\n" % self.getParticipants()
        out += "Promoted by: %s\n" % self.getPromoter()
        return out

    def toProtocolTreeNode(self):
        node = super(PromotedGroupNotificationProtocolEntity, self).toProtocolTreeNode()
        promoteNode = ProtocolTreeNode("promote")
        participants = []
        for jid, _type in self.getParticipants().items():
            pnode = ProtocolTreeNode("participant", {"jid": jid})
            if _type:
                pnode["type"] = _type
            participants.append(pnode)

        promoteNode.addChildren(participants)
        node.addChild(promoteNode)
        return node

    @staticmethod
    def fromProtocolTreeNode(node):
        promoteNode = node.getChild("promote")
        participants = {}
        for p in promoteNode.getAllChildren("participant"):
            participants[p["jid"]] = p["type"]

        entity = GroupsNotificationProtocolEntity.fromProtocolTreeNode(node)
        entity.__class__ = PromotedGroupNotificationProtocolEntity
        entity.setParticipantsData(participants)
        return entity