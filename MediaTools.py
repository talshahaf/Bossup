import hashlib, os, io, socket, ssl, mimetypes, sys, base64, time
from PIL import Image

if sys.version_info >= (3, 0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen
    
from yowsup.common.http.waresponseparser import JSONResponseParser
from yowsup.common import YowConstants

from yowsup.layers.protocol_media.protocolentities     import ImageDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities     import DownloadableMediaMessageProtocolEntity

class MediaTools:

    @classmethod
    def MediaDownload(cls, url):
        u = urlopen(url)
        finalfile = b''
        
        meta = u.info()

        if sys.version_info >= (3, 0):
            fileSize = int(u.getheader("Content-Length"))
        else:
            fileSize = int(meta.getheaders("Content-Length")[0])

        fileSizeDl = 0
        blockSz = 8192
        while True:
            buf = u.read(blockSz)

            if not buf:
                break

            fileSizeDl += len(buf)
            finalfile += buf
         
        name = url[url.rfind('/')+1:]
        return name, finalfile
        
    @classmethod
    def MediaUpload(cls, fromjid, tojid, filename, filedata, uploadUrl, userAgent):
        sock = socket.socket()
        _host = uploadUrl.replace("https://","")

        url = _host[:_host.index('/')]
        port = 443

        filetype = mimetypes.guess_type(filename)[0]
        filesize = len(filedata)

        sock.connect((url, port))
        ssl_sock = ssl.wrap_socket(sock)

        m = hashlib.md5()
        m.update(filename.encode())
        crypto = m.hexdigest() + os.path.splitext(filename)[1]

        boundary = "zzXXzzYYzzXXzzQQ"#"-------" + m.hexdigest() #"zzXXzzYYzzXXzzQQ"
        contentLength = 0

        hBAOS = "--" + boundary + "\r\n"
        hBAOS += "Content-Disposition: form-data; name=\"to\"\r\n\r\n"
        hBAOS += tojid.replace("@whatsapp.net","").replace("@g.us","") + "\r\n"
        hBAOS += "--" + boundary + "\r\n"
        hBAOS += "Content-Disposition: form-data; name=\"from\"\r\n\r\n"
        hBAOS += fromjid.replace("@whatsapp.net","") + "\r\n"

        hBAOS += "--" + boundary + "\r\n"
        hBAOS += "Content-Disposition: form-data; name=\"file\"; filename=\"" + crypto + "\"\r\n"
        hBAOS  += "Content-Type: " + filetype + "\r\n\r\n"

        fBAOS = "\r\n--" + boundary + "--\r\n"

        contentLength += len(hBAOS)
        contentLength += len(fBAOS)
        contentLength += filesize

        POST = "POST %s\r\n" % uploadUrl
        POST += "Content-Type: multipart/form-data; boundary=" + boundary + "\r\n"
        POST += "Host: %s\r\n" % url
        POST += "User-Agent: %s\r\n" % userAgent
        POST += "Content-Length: " + str(contentLength) + "\r\n\r\n"

        ssl_sock.send(bytearray(POST.encode()))
        ssl_sock.send(bytearray(hBAOS.encode()))

        totalsent = 0
        buf = 1024
        stream = filedata

        logcount = 0
        while totalsent < int(filesize):
            if logcount > 10:
                logcount = 0
                print('{}/{}'.format(totalsent, int(filesize)))
            logcount += 1
            ssl_sock.send(stream[:buf])
            stream = stream[buf:]
            totalsent = totalsent + buf

        ssl_sock.send(bytearray(fBAOS.encode()))

        data = ssl_sock.recv(8192)
        data += ssl_sock.recv(8192)
        data += ssl_sock.recv(8192)
        data += ssl_sock.recv(8192)
        data += ssl_sock.recv(8192)
        data += ssl_sock.recv(8192)
        data += ssl_sock.recv(8192)
        lines = data.decode().splitlines()


        result = None

        pvars = ["name", "type", "size", "url", "error", "mimetype", "filehash", "width", "height"]
        parser = JSONResponseParser()
        
        for l in lines:
            if l.startswith("{"):
                result = parser.parse(l, pvars)
                break

        if not result:
            raise Exception("json data not found")

        return result["url"]
    
    @classmethod
    def generateIdentity(cls):
        return os.urandom(20)

    @classmethod
    def getFileHashForUpload(cls, filedata):
        sha1 = hashlib.sha256()
        sha1.update(filedata)
        b64Hash = base64.b64encode(sha1.digest())
        return b64Hash if type(b64Hash) is str else b64Hash.decode()

    @classmethod
    def createImageUploadMedia(cls, jid, name, fileName, fileData, url, ip, caption = None):
        preview = cls.generatePreviewFromImage(fileData)
        width, height = cls.getImageDimensions(fileData)
        entity = DownloadableMediaMessageProtocolEntity(DownloadableMediaMessageProtocolEntity.MEDIA_TYPE_IMAGE, mimetypes.guess_type(fileName)[0], cls.getFileHashForUpload(fileData), url, ip, len(fileData), fileName, to = jid, notify = name, preview = preview)
        entity.__class__ = ImageDownloadableMediaMessageProtocolEntity
        entity.setImageProps("raw", width, height, caption)
        return entity
        
    @classmethod
    def createAudioUploadMedia(cls, jid, name, fileName, fileData, url, ip):
        return DownloadableMediaMessageProtocolEntity(DownloadableMediaMessageProtocolEntity.MEDIA_TYPE_AUDIO, mimetypes.guess_type(fileName)[0], cls.getFileHashForUpload(fileData), url, ip, len(fileData), fileName, to = jid, notify = name)
    
    @classmethod
    def scaleImage(cls, fileData, width, height):
        memimg = io.BytesIO(fileData)
        im = Image.open(memimg)
        im.thumbnail((width, height))
        outfile = io.BytesIO()
        im.save(outfile, im.format)
        outfile.seek(0)
        return outfile.read()
        
    @classmethod
    def resizeImage(cls, imgdata, w, h):
        b = io.BytesIO(imgdata)
        src = Image.open(b)
        return bytearray(src.resize((w, h)).tostring("jpeg", "RGB"))
        
    @classmethod
    def getImageDimensions(cls, fileData):
        memimg = io.BytesIO(fileData)
        im = Image.open(memimg)
        return im.size
        
    @classmethod
    def generatePreviewFromImage(cls, filedata):
        return cls.scaleImage(filedata, YowConstants.PREVIEW_WIDTH, YowConstants.PREVIEW_HEIGHT)
