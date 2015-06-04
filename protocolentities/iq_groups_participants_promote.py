from yowsup.structs import ProtocolEntity, ProtocolTreeNode
from yowsup.layers.protocol_groups.protocolentities.iq_groups_v2 import GroupsV2IqProtocolEntity


class PromoteParticipantsIqProtocolEntity(GroupsV2IqProtocolEntity):
    '''
    <iq type="set" id="{{id}}" xmlns="w:g", to="{{group_jid}}">
        <promote>
            <participant jid="{{jid}}"></participant>
            <participant jid="{{jid}}"></participant>
        </promote>
    </iq>
    '''

    def __init__(self, group_jid, participantList, _id = None):
        super(PromoteParticipantsIqProtocolEntity, self).__init__(to = group_jid, _id = _id, _type = "set")
        self.setProps(group_jid, participantList)

    def setProps(self, group_jid, participantList):
        assert type(participantList) is list, "Must be a list of jids, got %s instead." % type(participantList)
        assert len(participantList), "Participant list cannot be empty"
        self.group_jid = group_jid
        self.participantList = participantList

    def toProtocolTreeNode(self):
        node = super(PromoteParticipantsIqProtocolEntity, self).toProtocolTreeNode()
        participantNodes = [
            ProtocolTreeNode("participant", {
                "jid":       participant
            })
            for participant in self.participantList
        ]
        node.addChild(ProtocolTreeNode("promote",{}, participantNodes))
        return node

    @staticmethod
    def fromProtocolTreeNode(node):
        entity = GroupsV2IqProtocolEntity.fromProtocolTreeNode(node)
        entity.__class__ = PromoteParticipantsIqProtocolEntity
        participantList = []
        for participantNode in node.getChild("promote").node.getAllChildren():
            participantList.append(participantNode["jid"])
        entity.setProps(node.getAttributeValue("to"), participantList)
        return entity
