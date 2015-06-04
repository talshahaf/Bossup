import datetime

class Media(object):
    def __init__(self, type, preview, name, data, **kwargs):
        self.type = type
        self.preview = preview
        self.name = name
        self.data = data
        for key,value in kwargs.iteritems():
            setattr(self, key, value)

class Participant:
    def __init__(self, id, admin):
        self.id = id
        self.admin = admin

class GroupInfo(object):
    def __init__(self, **kwargs):
        allowed = ['id', 'owner', 'subject', 'subject_owner', 'subject_time', 'creation_time', 'participants']
        for k,v in kwargs.items():
            if k in allowed:
                setattr(self, k, v)

class Handler:
    def __init__(self, layer, entity):
        self.entity = entity
        self.layer = layer

    def SendText(self, jid, self_name, data):
        self.layer.post(self.layer.SendTextMessage, jid, self_name, data)
        
    def ReceiveText(self, jid, timestamp, from_id, from_name, data):
        if jid == from_id:
            self.layer.deferredPost(self.entity.ReceiveText, datetime.datetime.fromtimestamp(timestamp), from_id, from_name, data)
        else:
            self.layer.deferredPost(self.entity.ReceiveGroupText, jid, datetime.datetime.fromtimestamp(timestamp), from_id, from_name, data)
        
    def ReceiveMedia(self, jid, timestamp, from_id, from_name, media):
        if jid == from_id:
            self.layer.deferredPost(self.entity.ReceiveMedia, datetime.datetime.fromtimestamp(timestamp), from_id, from_name, media)
        else:
            self.layer.deferredPost(self.entity.ReceiveGroupMedia, jid, datetime.datetime.fromtimestamp(timestamp), from_id, from_name, media)
        
    def GetOwnNumber(self):
        return self.layer.GetOwnNumber()
        
    def SendVCard(self, jid, name, number, imgdata_gif = None):
        self.layer.post(self.layer.SendVCard, jid, name, number, imgdata_gif)
        
    def SendLocation(self, jid, lat, lon, name = None, url = None):
        self.layer.post(self.layer.SendLocation, jid, lat, lon, name, url)
        
    def registerDestructor(self, dest):
        self.layer.post(self.layer.registerDestructor, dest)
        
    def BroadcastEvent(self, ev):
        return self.layer.BroadcastEvent(ev)
        
    def OnEvent(self, ev):
        self.layer.deferredPost(self.entity.OnEvent, ev)
        
    def CreateGroup(self, subject, cb = None, arg = None):
        self.layer.post(self.layer.CreateGroup, subject, cb, arg)
        
    def AddToGroup(self, gid, uids, cb = None, arg = None):
        self.layer.post(self.layer.AddToGroup, gid, uids, cb, arg)
        
    def RemoveFromGroup(self, gid, uids, cb = None, arg = None):
        self.layer.post(self.layer.RemoveFromGroup, gid, uids, cb, arg)
        
    def LeaveGroup(self, gid):
        self.layer.post(self.layer.LeaveGroup, gid)
        
    def ListGroups(self, cb = None, arg = None):
        self.layer.post(self.layer.ListGroups, cb, arg)
        
    def GetGroupInfo(self, gid, cb = None, arg = None):
        self.layer.post(self.layer.GetGroupInfo, gid, cb, arg)
        
    def OnGroupCreated(self, group):
        self.layer.deferredPost(self.entity.OnGroupCreated, group)
        
    def OnGroupSubjectChanged(self, gid, subject):
        self.layer.deferredPost(self.entity.OnGroupSubjectChanged, gid, subject)
        
    def OnGroupPictureChanged(self, gid):
        self.layer.deferredPost(self.entity.OnGroupPictureChanged, gid)
    
    def GetProfileImage(self, jid, cb = None, arg = None):
        self.layer.post(self.layer.GetProfileImage, jid, cb, arg)
        
    def SetProfileImage(self, jid, img):
        self.layer.post(self.layer.SetProfileImage, jid, img)
        
    def SendBroadcastMessage(self, jids, message):
        self.layer.post(self.layer.SendBroadcastMessage, jids, message)
        
    def SetStatus(self, status):
        self.layer.post(self.layer.SetStatus, status)
        
    def post(self, func, *args, **kwargs):
        self.layer.post(func, *args, **kwargs)
        
    def deferredPost(self, func, *args, **kwargs):
        self.layer.deferredPost(func, *args, **kwargs)
        
    def SendImage(self, jid, name, fileName, fileData, caption, cb = None, arg = None):
        self.layer.post(self.layer.SendImage, jid, name, fileName, fileData, caption = caption, cb = cb, arg = arg)
        
    def SendAudio(self, jid, name, fileName, fileData, cb = None, arg = None):
        self.layer.post(self.layer.SendAudio, jid, name, fileName, fileData, cb = cb, arg = arg)
            
    def OnGroupParticipantAdded(self, gid, participants):
        self.layer.deferredPost(self.entity.OnGroupParticipantAdded, gid, participants)
        
    def OnGroupParticipantRemoved(self, gid, participants):
        self.layer.deferredPost(self.entity.OnGroupParticipantRemoved, gid, participants)
        
    def OnGroupParticipantPromoted(self, gid, participants):
        self.layer.deferredPost(self.entity.OnGroupParticipantPromoted, gid, participants)
        
    def MakeAdmin(self, gid, uids, cb = None, arg = None):
        self.layer.post(self.layer.MakeAdmin, gid, uids, cb, arg)
        
class Entity(object):
    
    def __init__(self):
        self.handlerClass = Handler
        
    def _initialize(self, handler):
        self.handler = handler
        self.initialize()
        
    def initialize(self):
        pass
        
    def ReceiveText(self, timestamp, from_id, from_name, data):
        pass
        
    def ReceiveMedia(self, timestamp, from_id, from_name, media):
        pass
        
    def ReceiveGroupText(self, gid, timestamp, from_id, from_name, data):
        pass
        
    def ReceiveGroupMedia(self, gid, timestamp, from_id, from_name, media):
        pass
        
    def SendText(self, jid, self_name, data):
        self.handler.SendText(jid, self_name, data)
        
    def GetOwnNumber(self):
        return self.handler.GetOwnNumber()
        
    def SendVCard(self, jid, name, number, imgdata_gif = None):
        self.handler.SendVCard(jid, name, number, imgdata_gif)
        
    def SendLocation(self, jid, lat, lon, name = None, url = None):
        self.handler.SendLocation(jid, lat, lon, name, url)
            
    def registerDestructor(self, dest):
        self.handler.registerDestructor(dest)
        
    def BroadcastEvent(self, ev):
        return self.handler.BroadcastEvent(ev)
        
    def OnEvent(self, ev):
        pass
    
    def CreateGroup(self, subject, cb, arg = None):
        self.handler.CreateGroup(subject, cb, arg)
        
    def AddToGroup(self, gid, uids, cb = None, arg = None):
        self.handler.AddToGroup(gid, uids, cb, arg)
        
    def RemoveFromGroup(self, gid, uids, cb = None, arg = None):
        self.handler.RemoveFromGroup(gid, uids, cb, arg)
        
    def LeaveGroup(self, gid):
        self.handler.LeaveGroup(gid)
        
    def ListGroups(self, cb, arg = None):
        self.handler.ListGroups(cb, arg)
        
    def GetGroupInfo(self, gid, cb, arg = None):
        self.handler.GetGroupInfo(gid, cb, arg)
        
    def OnGroupCreated(self, group):
        pass
        
    def OnGroupSubjectChanged(self, gid, subject):
        pass
        
    def OnGroupPictureChanged(self, gid):
        pass
        
    def GetProfileImage(self, jid, cb, arg = None):
        self.handler.GetProfileImage(jid, cb, arg)
        
    def SetProfileImage(self, jid, img):
        self.handler.SetProfileImage(jid, img)
        
    def SendBroadcastMessage(self, jids, message):
        self.handler.SendBroadcastMessage(jids, message)
        
    def SetStatus(self, status):
        self.handler.SetStatus(status)
        
    def post(self, func, *args, **kwargs):
        self.handler.post(func, *args, **kwargs)
        
    def SendImage(self, jid, name, fileName, fileData, caption, cb = None, arg = None):
        self.handler.SendImage(jid, name, fileName, fileData, caption = caption, cb = cb, arg = arg)
        
    def SendAudio(self, jid, name, fileName, fileData, cb = None, arg = None):
        self.handler.SendAudio(jid, name, fileName, fileData, cb = cb, arg = arg)
        
    def OnGroupParticipantAdded(self, gid, participants):
        pass
        
    def OnGroupParticipantRemoved(self, gid, participants):
        pass
        
    def OnGroupParticipantPromoted(self, gid, participants):
        pass
        
    def MakeAdmin(self, gid, uids, cb = None, arg = None):
        self.handler.MakeAdmin(gid, uids, cb, arg)
        
    def deferredPost(self, func, *args, **kwargs):
        self.handler.deferredPost(func, *args, **kwargs)
        
        
class SpecificHandler:
    def __init__(self, layer, entity, jid):
        self.entity = entity
        self.layer = layer
        self.jid = jid

    def SendText(self, jid, self_name, data):
        self.layer.post(self.layer.SendTextMessage, jid, self_name, data)
        
    def ReceiveText(self, jid, timestamp, from_id, from_name, data):
        if self.jid != jid:
            return
        if jid == from_id:
            self.layer.deferredPost(self.entity.ReceiveText, datetime.datetime.fromtimestamp(timestamp), from_id, from_name, data)
        else:
            self.layer.deferredPost(self.entity.ReceiveGroupText, jid, datetime.datetime.fromtimestamp(timestamp), from_id, from_name, data)
        
    def ReceiveMedia(self, jid, timestamp, from_id, from_name, media):
        if self.jid != jid:
            return
        if jid == from_id:
            self.layer.deferredPost(self.entity.ReceiveMedia, datetime.datetime.fromtimestamp(timestamp), from_id, from_name, media)
        else:
            self.layer.deferredPost(self.entity.ReceiveGroupMedia, jid, datetime.datetime.fromtimestamp(timestamp), from_id, from_name, media)
        
    def GetOwnNumber(self):
        return self.layer.GetOwnNumber()
        
    def SendVCard(self, jid, name, number, imgdata_gif = None):
        self.layer.post(self.layer.SendVCard, jid, name, number, imgdata_gif)
        
    def SendLocation(self, jid, lat, lon, name = None, url = None):
        self.layer.post(self.layer.SendLocation, jid, lat, lon, name, url)
        
    def registerDestructor(self, dest):
        self.layer.post(self.layer.registerDestructor, dest)
        
    def BroadcastEvent(self, ev):
        return self.layer.BroadcastEvent(ev)
        
    def OnEvent(self, ev):
        self.layer.deferredPost(self.entity.OnEvent, ev)
        
    def CreateGroup(self, subject, cb = None, arg = None):
        self.layer.post(self.layer.CreateGroup, subject, cb, arg)
        
    def AddToGroup(self, gid, uids, cb = None, arg = None):
        self.layer.post(self.layer.AddToGroup, gid, uids, cb, arg)
        
    def RemoveFromGroup(self, gid, uids, cb = None, arg = None):
        self.layer.post(self.layer.RemoveFromGroup, gid, uids, cb, arg)
        
    def LeaveGroup(self, gid):
        self.layer.post(self.layer.LeaveGroup, gid)
        
    def ListGroups(self, cb = None, arg = None):
        self.layer.post(self.layer.ListGroups, cb, arg)
        
    def GetGroupInfo(self, gid, cb = None, arg = None):
        self.layer.post(self.layer.GetGroupInfo, gid, cb, arg)
        
    def OnGroupCreated(self, group):
        if self.jid != group.id:
            return
        self.layer.deferredPost(self.entity.OnGroupCreated, group)
        
    def OnGroupSubjectChanged(self, gid, subject):
        if self.jid != gid:
            return
        self.layer.deferredPost(self.entity.OnGroupSubjectChanged, gid, subject)
        
    def OnGroupPictureChanged(self, gid):
        if self.jid != gid:
            return
        self.layer.deferredPost(self.entity.OnGroupPictureChanged, gid)
    
    def GetProfileImage(self, jid, cb = None, arg = None):
        self.layer.post(self.layer.GetProfileImage, jid, cb, arg)
        
    def SetProfileImage(self, jid, img):
        self.layer.post(self.layer.SetProfileImage, jid, img)
        
    def SendBroadcastMessage(self, jids, message):
        self.layer.post(self.layer.SendBroadcastMessage, jids, message)
        
    def SetStatus(self, status):
        self.layer.post(self.layer.SetStatus, status)
        
    def post(self, func, *args, **kwargs):
        self.layer.post(func, *args, **kwargs)
        
    def deferredPost(self, func, *args, **kwargs):
        self.layer.deferredPost(func, *args, **kwargs)
        
    def SendImage(self, jid, name, fileName, fileData, caption, cb = None, arg = None):
        self.layer.post(self.layer.SendImage, jid, name, fileName, fileData, caption = caption, cb = cb, arg = arg)
        
    def SendAudio(self, jid, name, fileName, fileData, cb = None, arg = None):
        self.layer.post(self.layer.SendAudio, jid, name, fileName, fileData, cb = cb, arg = arg)
            
    def OnGroupParticipantAdded(self, gid, participants):
        if self.jid != gid:
            return
        self.layer.deferredPost(self.entity.OnGroupParticipantAdded, gid, participants)
        
    def OnGroupParticipantRemoved(self, gid, participants):
        if self.jid != gid:
            return
        self.layer.deferredPost(self.entity.OnGroupParticipantRemoved, gid, participants)
        
    def OnGroupParticipantPromoted(self, gid, participants):
        if self.jid != gid:
            return
        self.layer.deferredPost(self.entity.OnGroupParticipantPromoted, gid, participants)
        
    def MakeAdmin(self, gid, uids, cb = None, arg = None):
        self.layer.post(self.layer.MakeAdmin, gid, uids, cb, arg)