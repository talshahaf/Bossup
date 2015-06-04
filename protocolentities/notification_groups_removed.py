from yowsup.structs import ProtocolEntity, ProtocolTreeNode
from yowsup.layers.protocol_notifications.protocolentities import NotificationProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.notification_groups import GroupsNotificationProtocolEntity

class RemovedGroupNotificationProtocolEntity(GroupsNotificationProtocolEntity):
    '''

    <notification notify="WhatsApp" id="{{id}}" t="{{TIMESTAMP}}" participant="{{PARTICIPANT_JID}}" from="{{GROUP_JID}}" type="w:gp2">
        <remove subject="{{subject}}">
            <participant type="admin" jid="{{JID_1}}">\n</participant>
            <participant jid="{{JID_2}}">\n</participant>
        </remove>
    </notification>

    '''

    def __init__(self, _type, _id,  _from, timestamp, notify, participant, subject, participants):
        super(RemovedGroupNotificationProtocolEntity, self).__init__(_id, _from, timestamp, notify, participant)
        self.setParticipantsData(subject, participants)

    def setParticipantsData(self, subject, participants):
        self.subject = subject
        self.participants = participants

    def getParticipants(self):
        return self.participants
        
    def getSubject(self):
        return self.subject
        
    def getRemover(self, full = True):
        return self.participant if full else self.participant.split('@')[0]

    def __str__(self):
        out = super(RemovedGroupNotificationProtocolEntity, self).__str__()
        out += "participants: %s\n" % self.getParticipants()
        out += "Removed by: %s\n" % self.getRemover()
        return out

    def toProtocolTreeNode(self):
        node = super(RemovedGroupNotificationProtocolEntity, self).toProtocolTreeNode()
        removeNode = ProtocolTreeNode("remove", {'subject': self.getSubject()})
        participants = []
        for jid, _type in self.getParticipants().items():
            pnode = ProtocolTreeNode("participant", {"jid": jid})
            if _type:
                pnode["type"] = _type
            participants.append(pnode)

        removeNode.addChildren(participants)
        node.addChild(removeNode)
        return node

    @staticmethod
    def fromProtocolTreeNode(node):
        removeNode = node.getChild("remove")
        participants = {}
        for p in removeNode.getAllChildren("participant"):
            participants[p["jid"]] = p["type"]

        entity = GroupsNotificationProtocolEntity.fromProtocolTreeNode(node)
        entity.__class__ = RemovedGroupNotificationProtocolEntity
        entity.setParticipantsData(removeNode["subject"], participants)
        return entity