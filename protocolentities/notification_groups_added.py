from yowsup.structs import ProtocolEntity, ProtocolTreeNode
from yowsup.layers.protocol_notifications.protocolentities import NotificationProtocolEntity
from yowsup.layers.protocol_groups.protocolentities.notification_groups import GroupsNotificationProtocolEntity

class AddedGroupNotificationProtocolEntity(GroupsNotificationProtocolEntity):
    '''

    <notification notify="WhatsApp" id="{{id}}" t="{{TIMESTAMP}}" participant="{{PARTICIPANT_JID}}" from="{{GROUP_JID}}" type="w:gp2">
        <add>
            <participant type="admin" jid="{{JID_1}}">\n</participant>
            <participant jid="{{JID_2}}">\n</participant>
        </add>
    </notification>

    '''

    def __init__(self, _type, _id,  _from, timestamp, notify, participant, participants):
        super(AddedGroupNotificationProtocolEntity, self).__init__(_id, _from, timestamp, notify, participant)
        self.setParticipantsData(participants)

    def setParticipantsData(self, participants):
        self.participants = participants

    def getParticipants(self):
        return self.participants
        
    def getAdder(self, full = True):
        return self.participant if full else self.participant.split('@')[0]

    def __str__(self):
        out = super(AddedGroupNotificationProtocolEntity, self).__str__()
        out += "New participants: %s\n" % self.getParticipants()
        out += "Added by: %s\n" % self.getAdder()
        return out

    def toProtocolTreeNode(self):
        node = super(AddedGroupNotificationProtocolEntity, self).toProtocolTreeNode()
        addNode = ProtocolTreeNode("add")
        participants = []
        for jid, _type in self.getParticipants().items():
            pnode = ProtocolTreeNode("participant", {"jid": jid})
            if _type:
                pnode["type"] = _type
            participants.append(pnode)

        addNode.addChildren(participants)
        node.addChild(addNode)
        return node

    @staticmethod
    def fromProtocolTreeNode(node):
        addNode = node.getChild("add")
        participants = {}
        for p in addNode.getAllChildren("participant"):
            participants[p["jid"]] = p["type"]

        entity = GroupsNotificationProtocolEntity.fromProtocolTreeNode(node)
        entity.__class__ = AddedGroupNotificationProtocolEntity
        entity.setParticipantsData(participants)
        return entity