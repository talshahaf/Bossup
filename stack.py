from yowsup.stacks import YowStack
from yowsup.layers import YowParallelLayer
from yowsup.layers import YowLayerEvent
from yowsup.layers.auth                        import YowCryptLayer, YowAuthenticationProtocolLayer, AuthError
from yowsup.layers.coder                       import YowCoderLayer
from yowsup.layers.network                     import YowNetworkLayer
from yowsup.layers.protocol_messages           import YowMessagesProtocolLayer
from yowsup.layers.protocol_media              import YowMediaProtocolLayer
from yowsup.layers.stanzaregulator             import YowStanzaRegulator
from yowsup.layers.protocol_receipts           import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks               import YowAckProtocolLayer
from yowsup.layers.logger                      import YowLoggerLayer
from yowsup.layers.axolotl                     import YowAxolotlLayer
from yowsup.layers.protocol_groups             import YowGroupsProtocolLayer
from yowsup.layers.protocol_presence           import YowPresenceProtocolLayer
from yowsup.layers.protocol_iq                 import YowIqProtocolLayer
from yowsup.layers.protocol_calls              import YowCallsProtocolLayer
from yowsup.layers.protocol_notifications      import YowNotificationsProtocolLayer
from yowsup.layers.protocol_profiles           import YowProfilesProtocolLayer
from yowsup.layers.protocol_chatstate          import YowChatstateProtocolLayer

from yowsup.common import YowConstants
from yowsup import env
from layer import *
import logging, traceback, datetime

from group_notification_layer import YowMyGroupsProtocolLayer

class YowsupEchoStack(object):
    def __init__(self, credentials, entities):
        logger = logging.StreamHandler()
        logger.setLevel(logging.DEBUG)
        logging.getLogger("yowsup.stacks.yowstack").addHandler(logger)
        
        env.CURRENT_ENV = env.AndroidYowsupEnv()
        layers = (
            EchoLayer, 
            
            YowParallelLayer([YowGroupsProtocolLayer, YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowReceiptProtocolLayer, YowAckProtocolLayer, YowMediaProtocolLayer, YowPresenceProtocolLayer, YowIqProtocolLayer, YowCallsProtocolLayer, YowNotificationsProtocolLayer, YowProfilesProtocolLayer, YowChatstateProtocolLayer, YowMyGroupsProtocolLayer]),
            #SniffLayer,
            YowAxolotlLayer,
            YowLoggerLayer,
            YowCoderLayer,
            YowCryptLayer,
            YowStanzaRegulator,
            YowNetworkLayer
        )

        self.stack = YowStack(layers)
        self.stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, credentials)
        self.stack.setProp(EchoLayer.PROP_SELFNUMBER, credentials[0])
        self.stack.setProp(EchoLayer.PROP_ENTITYCLASSES, entities)
        self.stack.setProp(EchoLayer.SELF_STACK, self.stack)
        self.stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])
        self.stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
        self.stack.setProp(YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource())

    def start(self):
        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        try:
            self.stack.loop()
        except AuthError as e:
            print("Authentication Error: %s" % e.message)

            
def main_server(creds, entities):
    logging.basicConfig()
    while True:
        print 'starting: {}'.format(datetime.datetime.now())
        try:
            stack = YowsupEchoStack(creds, entities)
            stack.start()
        except Exception:
            print traceback.format_exc('')
        for destructor in EchoLayer.destructors:
            try:
                destructor()
            except Exception:
                print traceback.format_exc('while destructing')
        EchoLayer.destructors = []
        time.sleep(5)