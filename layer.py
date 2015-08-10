import threading, logging, pprint, time, types, datetime, base64, os, traceback, sys

from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers                                     import YowLayer
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities     import DownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities     import ImageDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities  import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_media.protocolentities     import LocationMediaMessageProtocolEntity
from yowsup.layers.protocol_acks.protocolentities      import OutgoingAckProtocolEntity
from yowsup.layers.protocol_media.protocolentities     import VCardMediaMessageProtocolEntity
from yowsup.layers.protocol_presence.protocolentities  import AvailablePresenceProtocolEntity
from yowsup.layers.protocol_groups.protocolentities    import *
from yowsup.layers.protocol_profiles.protocolentities  import *
from yowsup.layers.protocol_messages.protocolentities  import BroadcastTextMessage
from yowsup.layers.protocol_chatstate.protocolentities import OutgoingChatstateProtocolEntity
from yowsup.layers.protocol_chatstate.protocolentities import ChatstateProtocolEntity
from yowsup.layers.protocol_media.protocolentities     import RequestUploadIqProtocolEntity
from yowsup.layers.protocol_media.mediauploader        import MediaUploader
from yowsup.layers import YowLayerEvent
from yowsup import env
    
import MessagingEntity
from MediaTools import *
from handler_thread import *

from protocolentities.notification_groups_promoted import *

logger = logging.getLogger(__name__)
        
class EchoLayer(YowInterfaceLayer):
    
    destructors = []
    ENTITIES = []
    PROP_SELFNUMBER = "special.my.prop.self.number"
    SELF_STACK = "special.my.prop.self.stack"
    PROP_ENTITYCLASSES = "special.my.prop.entity"
    
    EVENT_RUNNABLE = "special.my.event.runnable"
    
    def __init__(self):
        super(EchoLayer, self).__init__()
        self.entities = []
        self.pending_requests = []
        self.pending_lock = threading.Condition()
        self.pending_sends = {}
        self.handlerThread = HandlerThread()
        self.downloadThread = HandlerThread()
    
    @ProtocolEntityCallback("success")
    def onSuccess(self, successProtocolEntity):
        self.self_id = self.getProp(self.__class__.PROP_SELFNUMBER, '')
        self.stack = self.getProp(self.__class__.SELF_STACK, None)
        self.__class__.ENTITIES = self.getProp(self.__class__.PROP_ENTITYCLASSES, None)
        for entity in self.__class__.ENTITIES:
            ent = entity()
            hand = ent.handlerClass(self, ent, ent.handlerArg)
            ent._initialize(hand)
            self.entities.append(hand)
        self.handlerThread.start()
        self.downloadThread.start()
        

            
    @ProtocolEntityCallback("iq")
    def onIq(self, iqProtocolEntity):
        tocall = []
        self.pending_lock.acquire()
        try:
            tocall = [pending for pending in self.pending_requests if (pending['overrideId'] if pending['overrideId'] else pending['entity'].getId()) == iqProtocolEntity.getId()]
            for c in tocall:
                self.pending_requests.remove(c)
        finally:
            self.pending_lock.release()
        for c in tocall:
            c['callback'](c['entity'], iqProtocolEntity, c['arg'])
            
    @ProtocolEntityCallback("notification")
    def onNotification(self, notificationProtocolEntity):
        if notificationProtocolEntity.getType() == 'w:gp2':
            
            dct = {
                        CreateGroupsNotificationProtocolEntity: None,
                        AddGroupsNotificationProtocolEntity: self.OnGroupParticipantAdded,
                        RemoveGroupsNotificationProtocolEntity: self.OnGroupParticipantRemoved,
                        PromotedGroupNotificationProtocolEntity: self.OnGroupParticipantPromoted,
                  }
                  
            if isinstance(notificationProtocolEntity, SubjectGroupsNotificationProtocolEntity):
                self.OnGroupSubjectChanged(notificationProtocolEntity.getFrom(), notificationProtocolEntity.getSubject())
            elif notificationProtocolEntity.__class__ in dct.keys():
                participants = {}
                for k in notificationProtocolEntity.getParticipants():
                    participants[k] = MessagingEntity.Participant(k, False)
                    
                if isinstance(notificationProtocolEntity, CreateGroupsNotificationProtocolEntity):
                    gid = notificationProtocolEntity.getGroupId()
                    groupInfo = MessagingEntity.GroupInfo(id = gid if gid.endswith('@g.us') else gid + '@g.us',
                                          owner = notificationProtocolEntity.getCreatorJid(), 
                                          subject = notificationProtocolEntity.getSubject(), 
                                          subject_owner = notificationProtocolEntity.getSubjectOwnerJid(), 
                                          subject_time = notificationProtocolEntity.getSubjectTimestamp(), 
                                          creation_time = notificationProtocolEntity.getCreationTimestamp(), 
                                          participants = participants)
                    self.OnGroupCreated(groupInfo)
                else:
                    dct[notificationProtocolEntity.__class__](notificationProtocolEntity.getFrom(), participants)
                
        elif notificationProtocolEntity.getFrom().endswith('@g.us') and notificationProtocolEntity.getType() == 'picture':
            self.OnGroupPictureChanged(notificationProtocolEntity)
            
    def sendRequest(self, requestEntity, callback, arg = None, overrideId = None):
        pending = {'entity':requestEntity, 'callback':callback, 'arg': arg, 'overrideId': overrideId}
        self.pending_lock.acquire()
        try:
            self.pending_requests.append(pending)
        finally:
            self.pending_lock.release()
        self.toLower(requestEntity)
        
    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        if messageProtocolEntity.getType() == 'text':
            if messageProtocolEntity.isGroupMessage():
                self.onGroupTextMessage(messageProtocolEntity)
            else:
                self.onTextMessage(messageProtocolEntity)
        elif messageProtocolEntity.getType() == 'media':
            if messageProtocolEntity.isGroupMessage():
                self.onGroupMediaMessage(messageProtocolEntity)
            else:
                self.onMediaMessage(messageProtocolEntity)
        else:
            self.reactToMessage(messageProtocolEntity)
    
    def waitHumanRandom(self):
        time.sleep(0.5)
        
    @ProtocolEntityCallback("receipt")
    def onReceipt(self, protocolEntity):
        #if protocolEntity.type == 'retry':
            #if protocolEntity.getId() in self.pending_sends:
            #    retry = self.pending_sends[protocolEntity.getId()]
            #    self.toLower(retry)
        #ack = OutgoingAckProtocolEntity(protocolEntity.getId(), "receipt", protocolEntity.getType(), protocolEntity.getFrom())
        self.toLower(protocolEntity.ack())
        
    @ProtocolEntityCallback("ack")
    def onAck(self, protocolEntity):
        if protocolEntity.getId() in self.pending_sends:
            del self.pending_sends[protocolEntity.getId()]
            return
    
    #------------------------------------------------------------------------------------------
                
    def onTextMessage(self, messageProtocolEntity):
        print('got from {} ({})'.format(messageProtocolEntity.getFrom(), messageProtocolEntity.getNotify()))
        self.reactToMessage(messageProtocolEntity)
        self.ReceiveText(messageProtocolEntity, group = False)
            
    def onGroupTextMessage(self, messageProtocolEntity):
        print('got group from {} - {} ({})'.format(messageProtocolEntity.getFrom(), messageProtocolEntity.getParticipant(), messageProtocolEntity.getNotify()))
        self.reactToMessage(messageProtocolEntity)
        self.ReceiveText(messageProtocolEntity, group = True)
                               
    def ReceiveText(self, messageProtocolEntity, group = False):
        for entity in self.entities:
            entity.ReceiveText(messageProtocolEntity.getFrom(), 
                               messageProtocolEntity.getTimestamp(),
                               messageProtocolEntity.getFrom() if not group else messageProtocolEntity.getParticipant(),
                               messageProtocolEntity.getNotify(), 
                               messageProtocolEntity.getBody())

    
    def onGroupMediaMessage(self, messageProtocolEntity):
        print('got group media from {} - {} ({})'.format(messageProtocolEntity.getFrom(), messageProtocolEntity.getParticipant(), messageProtocolEntity.getNotify()))
        self.reactToMessage(messageProtocolEntity)
        self.ReceiveMedia(messageProtocolEntity, group = True)
        
    def onMediaMessage(self, messageProtocolEntity):
        print('got media from {} ({})'.format(messageProtocolEntity.getFrom(), messageProtocolEntity.getNotify()))
        self.reactToMessage(messageProtocolEntity)
        self.ReceiveMedia(messageProtocolEntity, group = False)
                                    
    def ReceiveMedia(self, messageProtocolEntity, group = False):
        if isinstance(messageProtocolEntity, DownloadableMediaMessageProtocolEntity):
            data = None
            filename = None
            def asyncDownload(self, messageProtocolEntity):
                filename, data = MediaTools.MediaDownload(messageProtocolEntity.getMediaUrl())
                def async_cb(self, filename, data, messageProtocolEntity):
                    media = MessagingEntity.Media(messageProtocolEntity.getMediaType(), messageProtocolEntity.getPreview(), filename, data)
                    for entity in self.entities:
                        entity.ReceiveMedia(messageProtocolEntity.getFrom(), 
                                            messageProtocolEntity.getTimestamp(), 
                                            messageProtocolEntity.getFrom() if not group else messageProtocolEntity.getParticipant(), 
                                            messageProtocolEntity.getNotify(), 
                                            media)
                                            
                self.post(async_cb, self, filename, data, messageProtocolEntity)
                
            self.downloadThread.post(asyncDownload, self, messageProtocolEntity)
            return
        elif isinstance(messageProtocolEntity, VCardMediaMessageProtocolEntity):
            data = messageProtocolEntity.getCardData()
            filename = 'vcard'
        elif isinstance(messageProtocolEntity, LocationMediaMessageProtocolEntity):
            data = '{}\n{}\n{}\n{}'.format(messageProtocolEntity.getLocationName(), messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getLocationURL())
            filename = 'location'
        
        media = MessagingEntity.Media(messageProtocolEntity.getMediaType(), messageProtocolEntity.getPreview(), filename, data)
        for entity in self.entities:
            entity.ReceiveMedia(messageProtocolEntity.getFrom(), 
                                messageProtocolEntity.getTimestamp(), 
                                messageProtocolEntity.getFrom() if not group else messageProtocolEntity.getParticipant(), 
                                messageProtocolEntity.getNotify(), 
                                media)
    #------------------------------------------------------------------------------------

    def reactToMessage(self, messageProtocolEntity):
        self.markReceived(messageProtocolEntity)
        self.waitHumanRandom()
        self.markOnline()
        self.markRead(messageProtocolEntity)

    def markReceived(self, messageProtocolEntity):
        self.toLower(messageProtocolEntity.ack())
        
    def markRead(self, messageProtocolEntity):
        self.toLower(messageProtocolEntity.ack(True))
        
    def markOnline(self):
        entity = AvailablePresenceProtocolEntity()
        self.toLower(entity)
            
    def SendTextMessage(self, gid, name, message):
        self.markOnline()
        self.waitHumanRandom()
        self.makeTyping(gid)
        self.waitHumanRandom()
        protocolEntity = TextMessageProtocolEntity(message, to = gid, notify = name)
        self.toLower(protocolEntity)
        self.makeStopTyping(gid)
        self.pending_sends[protocolEntity.getId()] = protocolEntity
            
    def GetOwnNumber(self):
        return self.self_id
        
    def SendVCard(self, gid, name, number, imgdata_gif = None):
        if not number:
            number = '0'
        mabye_gif = 'PHOTO;ENCODING=BASE64;TYPE=GIF:{gifdata}\r\n'.format(gifdata=base64.b64encode(imgdata_gif)) if imgdata_gif else ''
        vcardTemplate = '''BEGIN:VCARD\r\nVERSION:3.0\r\nN:;{name};;;\r\nFN:{name}\r\nitem1.TEL:{number}\r\nitem1.X-ABLabel:Mobile\r\n{mabye_gif}END:VCARD'''
        outVcard = VCardMediaMessageProtocolEntity(name, vcardTemplate.format(name = name, number = self.formatNumber(number), mabye_gif=mabye_gif), to = gid)
        self.toLower(outVcard)
        
    def SendLocation(self, jid, lat, lon, name = None, url = None):
        entity = LocationMediaMessageProtocolEntity(lat, lon, name, url, 'raw', to = jid)
        self.toLower(entity)
        
    def SendImage(self, jid, name, fileName, fileData, caption = None, cb = None, arg = None):
        self.SendMedia('image', jid, name, fileName, fileData, cb, arg, caption = caption)
        
    def SendAudio(self, jid, name, fileName, fileData, cb = None, arg = None):
        self.SendMedia('audio', jid, name, fileName, fileData, cb, arg)
    
    def SendMedia(self, mediaType, jid, name, fileName, fileData, cb = None, arg = None, **kwargs):
        argument = kwargs
        toadd = {'mediaType': mediaType, 'jid': jid, 'name': name, 'fileName': fileName, 'fileData': fileData, 'cb': cb, 'arg': arg}
        for k,v in toadd.iteritems():
            argument[k] = v
        if mediaType not in ["image", "video", "audio"]:
            raise Exception("unknown media")
        entity = RequestUploadIqProtocolEntity(mediaType, b64Hash = MediaTools.getFileHashForUpload(fileData), size = len(fileData))
        self.sendRequest(entity, self.onSendMediaResult, argument)
    
    def onSendMediaResult(self, request, response, arg):
        def doneAsyncUpload(self, mediaType, tojid, name, fileName, fileData, url, ip, kwargs, cb, arg):
            if mediaType == 'image':
                entity = MediaTools.createImageUploadMedia(tojid, name, fileName, fileData, url, ip, kwargs.get('caption'))
            elif mediaType == 'audio':
                entity = MediaTools.createAudioUploadMedia(tojid, name, fileName, fileData, url, ip)
            elif mediaType == 'video':
                #entity = MediaTools.createAudioUploadMedia(tojid, name, fileName, fileData, url, ip)
                raise Exception('not supported')
                
            self.toLower(entity)
            if cb:
                cb(arg)
            
        def asyncUpload(self, response, arg):
            url = MediaTools.MediaUpload(self.getOwnJid().replace('@whatsapp.net', ''), arg['jid'], arg['fileName'], arg['fileData'], response.getUrl(), env.CURRENT_ENV.getUserAgent())
            self.post(doneAsyncUpload, self, arg['mediaType'], arg['jid'], arg['name'], arg['fileName'], arg['fileData'], url, response.getIp(), arg, arg['cb'], arg['arg'])
         
        if response.isDuplicate():
            doneAsyncUpload(self, arg['mediaType'], arg['jid'], arg['name'], arg['fileName'], arg['fileData'], response.getUrl(), response.getIp(), arg, arg['cb'], arg['arg'])
        else:
            self.downloadThread.post(asyncUpload, self, response, arg)
        
    def formatNumber(self, number):
        rn = number[::-1]
        fourth = ''
        third1 = ''
        third2 = ''
        one = ''
        if len(rn) > 4:
            fourth = '-' 
        if len(rn) > 7:
            third1 = '-'
        if len(rn) > 10:
            third2 = '-'
            one = '+'
        return (rn[:4]+fourth+rn[4:7]+third1+rn[7:10]+third2+rn[10:]+one)[::-1]
        
    def registerDestructor(self, dest):
        if dest not in EchoLayer.destructors:
            EchoLayer.destructors.append(dest)
        
    def GetStack(self):
        return self.stack
        
    def onEvent(self, ev):
        if ev.getName() == self.__class__.EVENT_RUNNABLE:
            try:
                ev.args['runnable'](*ev.args['args'], **ev.args['kwargs'])
            except Exception:
                print('error at event runnable')
                print(traceback.format_exc())
            return
        for entity in self.entities:
            entity.OnEvent(ev.getName())
            
    def post(self, func, *args, **kwargs):
        return self.stack.broadcastEvent(YowLayerEvent(self.__class__.EVENT_RUNNABLE, runnable = func, args = args, kwargs = kwargs))
        
    def deferredPost(self, func, *args, **kwargs):
        self.handlerThread.post(func, *args, **kwargs)
            
    def BroadcastEvent(self, ev):
        return self.stack.broadcastEvent(YowLayerEvent(ev))   
        
    def CreateGroup(self, subject, cb, arg = None):
        argument = {'cb': cb, 'arg': arg}
        entity = CreateGroupsIqProtocolEntity(subject)
        self.sendRequest(entity, self.onGroupCreateResult, argument)
        
    def AddToGroup(self, gid, uids, cb, arg = None):
        lst_uid = list(uids)
        argument = {'gid':gid, 'uids':lst_uid, 'cb': cb, 'arg': arg}
        entity = AddParticipantsIqProtocolEntity(gid, lst_uid)
        self.sendRequest(entity, self.onParticipantsAddSuccess, argument)
        
    def LeaveGroup(self, gid):
        entity = LeaveGroupsIqProtocolEntity([gid])
        self.toLower(entity)
        
    def MakeAdmin(self, gid, uids, cb, arg = None):
        lst_uid = list(uids)
        argument = {'cb': cb, 'arg': arg}
        entity = PromoteParticipantsIqProtocolEntity(gid, lst_uid)
        self.sendRequest(entity, self.onMakeAdminSuccess, argument)
        
    def ListGroups(self, cb, arg = None):
        argument = {'cb': cb, 'arg': arg}
        entity = ListGroupsIqProtocolEntity()
        self.sendRequest(entity, self.onListGroups, argument)
        
    def RemoveFromGroup(self, gid, uids, cb, arg = None):
        lst_uid = list(uids)
        argument = {'gid':gid, 'uids':lst_uid, 'cb': cb, 'arg': arg}
        entity = RemoveParticipantsIqProtocolEntity(gid, lst_uid)
        self.sendRequest(entity, self.onParticipantsRemoveSuccess, argument)
        
    def GetGroupInfo(self, gid, cb, arg = None):
        argument = {'cb': cb, 'arg': arg}
        entity = InfoGroupsIqProtocolEntity(gid)
        self.sendRequest(entity, self.onGroupInfo, argument, overrideId = gid)
        
    def onGroupCreateResult(self, request, response, arg):
        if isinstance(response, SuccessCreateGroupsIqProtocolEntity):
            gid = response.groupId
            if not gid.endswith('@g.us'):
                gid += '@g.us'
            if arg['cb']:
                arg['cb'](gid, arg['arg'])
        else:
            print('error creating group')
            
    def onParticipantsAddSuccess(self, request, response, arg):
        if isinstance(response, SuccessAddParticipantsIqProtocolEntity):
            if arg['cb']:
                arg['cb'](response.groupId, response.participantList, arg['arg'])
        else:
            print('error adding to group')
    
    def onParticipantsRemoveSuccess(self, request, response, arg):
        if isinstance(response, SuccessRemoveParticipantsIqProtocolEntity):
            if arg['cb']:
                arg['cb'](response.groupId, response.participantList, arg['arg'])
        else:
            print('error removing from group')
            
    def onListGroups(self, request, response, arg):
        if isinstance(response, ListGroupsResultIqProtocolEntity):
            grps = []
            for g in response.groupsList:
                grps.append(MessagingEntity.GroupInfo(id = g.getId() if g.getId().endswith('@g.us') else g.getId() + '@g.us', 
                                      owner = g.getOwner(), 
                                      subject = g.getSubject(), 
                                      subject_owner = g.getSubjectOwner(), 
                                      subject_time = g.getSubjectTime(), 
                                      creation_time = g.getCreationTime(), 
                                      participants = {}))
            if arg['cb']:
                arg['cb'](grps, arg['arg'])
        else:
            print('error listing groups')
        
    def onGroupInfo(self, request, response, arg):
        if isinstance(response, InfoGroupsResultIqProtocolEntity):
            participants = {}
            for k, v in response.getParticipants().items():
                participants[k] = MessagingEntity.Participant(k, v == InfoGroupsResultIqProtocolEntity.TYPE_PARTICIPANT_ADMIN)
            groupInfo = MessagingEntity.GroupInfo(id = response.getGroupId(), 
                                  owner = response.getCreatorJid(), 
                                  subject = response.getSubject(), 
                                  subject_owner = response.getSubjectOwnerJid(), 
                                  subject_time = response.getSubjectTimestamp(), 
                                  creation_time = response.getCreationTimestamp(), 
                                  participants = participants)
            if arg['cb']:
                arg['cb'](groupInfo, arg['arg'])                      
        else:
            print('error infoing group')
    
    def onMakeAdminSuccess(self, request, response, arg):
        if arg['cb']:
            arg['cb'](response.groupId, response.participantList, arg['arg'])
        
    def OnGroupCreated(self, group):
        for entity in self.entities:
            entity.OnGroupCreated(group)
            
    def OnGroupPictureChanged(self, notificationProtocolEntity):
        for entity in self.entities:
            entity.OnGroupPictureChanged(notificationProtocolEntity.getFrom())
            
    def OnGroupSubjectChanged(self, gid, subject):
        for entity in self.entities:
            entity.OnGroupSubjectChanged(gid, subject)
            
    def OnGroupParticipantAdded(self, gid, participants):
        for entity in self.entities:
            entity.OnGroupParticipantAdded(gid, participants)
            
    def OnGroupParticipantRemoved(self, gid, participants):
        for entity in self.entities:
            entity.OnGroupParticipantRemoved(gid, participants)
    
    def OnGroupParticipantPromoted(self, gid, participants):
        for entity in self.entities:
            entity.OnGroupParticipantPromoted(gid, participants)
            
    def GetProfileImage(self, jid, cb, arg = None):
        argument = {'cb': cb, 'arg': arg}
        entity = GetPictureIqProtocolEntity(jid)
        self.sendRequest(entity, self.onProfileImage, argument)
        
    def onProfileImage(self, request, response, arg):
        if isinstance(response, ResultGetPictureIqProtocolEntity):
            if arg['cb']:
                arg['cb'](response.getPictureData(), arg['arg'])
        else:
            print('error getting image')
            
    def SetProfileImage(self, jid, img):
        entity = SetPictureIqProtocolEntity(jid, MediaTools.resizeImage(img, 96, 96), MediaTools.resizeImage(img, 640, 640))
        self.toLower(entity)
        
    def SendBroadcastMessage(self, jids, message):
        lst = list(jids)
        entity = BroadcastTextMessage(lst, message)
        self.toLower(entity)
        self.pending_sends[entity.getId()] = entity

    def SetStatus(self, status):
        entity = SetStatusIqProtocolEntity(status)
        self.toLower(entity)
        
    def makeTyping(self, jid):
        entity = OutgoingChatstateProtocolEntity(ChatstateProtocolEntity.STATE_TYPING, jid)
        self.toLower(entity)
        
    def makeStopTyping(self, jid):
        entity = OutgoingChatstateProtocolEntity(ChatstateProtocolEntity.STATE_PAUSED, jid)
        self.toLower(entity)
        
    #############################################################################################################


class SniffLayer(YowLayer):
    def send(self, entity):
        pprint.pprint('out: '+str(entity))
        self.toLower(entity)

    def receive(self, entity):
        pprint.pprint('in: '+str(entity))
        self.toUpper(entity)
        