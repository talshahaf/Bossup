import MessagingEntity
import stack


class MyGroup(MessagingEntity.Entity):
    MY_GID = 'xxx@g.us'
    
    # called after a successful connection
    def initialize(self):
        pass
        
    #user sent a text (after id filtering if specified)
    def ReceiveText(self, timestamp, from_id, from_name, data):
        pass
        
    #user sent media (not text) (see media object) (after id filtering if specified)
    def ReceiveMedia(self, timestamp, from_id, from_name, media):
        pass

    #specifing handler and gid (if handler is specific)
    def __init__(self):
        super(MyGroup, self).__init__()
        
        specific_id = True
        
        if specific_id:
            #specific id
            self.handlerClass = MessagingEntity.SpecificHandler # SPECIFIC UID/GID
            self.handlerArg = MyGroup.MY_GID # SPECIFIC UID/GID
        else:
            #any id
            self.handlerClass = MessagingEntity.Handler
    
    #group sent a text (after id filtering if specified)
    def ReceiveGroupText(self, gid, timestamp, from_id, from_name, data):
        pass
      
    #group sent media (not text) (see media object) (after id filtering if specified)
    def ReceiveGroupMedia(self, gid, timestamp, from_id, from_name, media):
        pass
    
    #self added to group or created a group (after id filtering if specified) (see group object)
    def OnGroupCreated(self, group):
        pass    
        
    #group name changed (after id filtering if specified)
    def OnGroupSubjectChanged(self, gid, subject):
        pass
      
    #group picture changed (after id filtering if specified)
    def OnGroupPictureChanged(self, gid):
        pass
    
    ############# participants events (participants = dictionary whose keys are the uids and the values are Participants object) ###########
    
    #participants added to group (after id filtering if specified)
    def OnGroupParticipantAdded(self, gid, participants):
        pass
    
    #participants removed from group (after id filtering if specified)
    def OnGroupParticipantRemoved(self, gid, participants):
        pass
    
    #participants were made admins in group (after id filtering if specified)
    def OnGroupParticipantPromoted(self, gid, participants):
        pass
    ##########################
    
    
    ####### methods ##########
    def example(self):
        # jid could be and user or any group
        # sends text to jid with name (if not in the recipient's contact list) containing text
        self.SendText(jid, name, text)
        #retrieves own phone number
        self.GetOwnNumber()
        #sends vcard (contact) to jid with name, the contact contains number and optionally imgdata_gif (the entire image file already read)
        self.SendVCard(jid, name, number, imgdata_gif = None)
        #sends a location (lat,lon) to jid, the location is called name with url
        self.SendLocation(jid, lat, lon, name = None, url = None)
        #destructorFunction will be called when the connection to the server closes
        self.registerDestructor(destructorFunction)
        #creates a group called subject, when the group is created cb is called with the new gid and the arg
        #cb signature is cb(gid, arg)
        self.CreateGroup(subject, cb, arg = None)
        #adds an iterable of uids to group optionally calling cb with arg with the result
        #cb signature is cb(gid, uids, arg), uids is a list of the uids added successfully
        self.AddToGroup(gid, uids, cb = None, arg = None)
        #removes an iterable of uids from group optionally calling cb with arg with the result
        #cb signature is cb(gid, uids, arg), uids is a list of the uids removed successfully
        self.RemoveFromGroup(gid, uids, cb = None, arg = None)
        #makes an iterable of uids group admins optionally calling cb with arg with the result
        #cb signature is cb(gid, uids, arg), uids is a list of the uids promoted successfully
        self.MakeAdmin(gid, uids, cb = None, arg = None)
        #leaves a group
        self.LeaveGroup(gid)
        #requests the list of groups (only if member of) calling cb with arg and the result
        #cb signature is cb(groups, arg) (groups is a list of Group object)
        self.ListGroups(cb, arg = None)
        #requests info for group calling cb with arg and the result
        #cb signature is cb(group, arg) (group is a Group object)
        self.GetGroupInfo(gid, cb, arg = None)
        #sets the profile image of a group (or self if jid == own number) to be img (which is the entire image file already read)
        self.SetProfileImage(jid, img)
        #sends the same message to a list of jids
        self.SendBroadcastMessage(jids, message)
        #sets the status. must be set on each successful connection to the server (should be called from initialize())
        self.SetStatus(status)
        #sends an image to jid with name, fileName is just the name of the file in the servers (and should end with the right extension according to the fileData's format), fileData is the entire image file already read, cb is called on result with arg
        #cb signature is cb(arg)
        self.SendImage(jid, name, fileName, fileData, caption, cb = None, arg = None)
        #identical to SendImage except for the caption
        self.SendAudio(jid, name, fileName, fileData, cb = None, arg = None)
        
        #####video upload is not yet supported#####
 
class FaceGroup(MessagingEntity.Entity):
    FACE_GID = 'yyy@g.us'
    FACE_NAME = 'face swapper'
    
    def __init__(self):
        super(FaceGroup, self).__init__()
        self.handlerClass = MessagingEntity.SpecificHandler
        self.handlerArg = FaceGroup.FACE_GID
        
    def ReceiveGroupMedia(self, gid, timestamp, from_id, from_name, media):
        newimg = doFaces(gid, media.data)
        if newimg:
            self.SendImage(FaceGroup.FACE_GID, FaceGroup.FACE_NAME, '{}.jpg'.format(int(time.time())), newimg, caption = '')
            
            
#    (phone,password)
CREDS = ("", "")

if __name__ == '__main__':
                            #list of entities (can overlap)
    stack.main_server(CREDS, [MyGroup, FaceGroup])