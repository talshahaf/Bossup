from yowsup.structs import ProtocolTreeNode
from yowsup.layers.protocol_iq.protocolentities import ResultIqProtocolEntity
class SuccessPromoteParticipantsIqProtocolEntity(ResultIqProtocolEntity):
    '''
    <iq type="result" from="{{group_jid}}" id="{{id}}">
        <promote type="success" participant="{{jid}}"></promote>
        <promote type="success" participant="{{jid}}"></promote>
    </iq>
    '''

    def __init__(self, _id, groupId, participantList):
        super(SuccessPromoteParticipantsIqProtocolEntity, self).__init__(_from = groupId, _id = _id)
        self.setProps(groupId, participantList)

    def setProps(self, groupId, participantList):
        self.groupId = groupId
        self.participantList = participantList
        self.action = 'promote'

    def getAction(self):
        return self.action

    def toProtocolTreeNode(self):
        node = super(SuccessPromoteParticipantsIqProtocolEntity, self).toProtocolTreeNode()
        participantNodes = [
            ProtocolTreeNode("promote", {
                "type":                     "success",
                "participant":       participant
            })
            for participant in self.participantList
        ]
        node.addChildren(participantNodes)

        return node

    @staticmethod
    def fromProtocolTreeNode(node):
        entity = ResultIqProtocolEntity.fromProtocolTreeNode(node)
        entity.__class__ = SuccessPromoteParticipantsIqProtocolEntity
        participantList = []
        for participantNode in node.getAllChildren():
            if participantNode["type"]=="success":
                participantList.append(participantNode["participant"])
        entity.setProps(node.getAttributeValue("from"), participantList)
        return entity
