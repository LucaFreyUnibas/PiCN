"""Fetch Tool for PiCN"""

from PiCN.LayerStack import LayerStack
from PiCN.Layers.SynchronisationLayer import BasicSynchronisationLayer, SynchronisationMessageDict
from PiCN.Layers.AutoconfigLayer import AutoconfigClientLayer
from PiCN.Layers.ChunkLayer import BasicChunkLayer
from PiCN.Layers.PacketEncodingLayer import BasicPacketEncodingLayer
from PiCN.Layers.ChunkLayer.Chunkifyer import SimpleContentChunkifyer
from PiCN.Layers.LinkLayer import BasicLinkLayer
from PiCN.Layers.LinkLayer.FaceIDTable import FaceIDDict
from PiCN.Layers.LinkLayer.Interfaces import UDP4Interface, AddressInfo
from PiCN.Processes.PiCNSyncDataStructFactory import PiCNSyncDataStructFactory
from PiCN.Layers.PacketEncodingLayer.Encoder import SimpleStringEncoder
from PiCN.Layers.PacketEncodingLayer.Encoder import BasicEncoder
from PiCN.Packets import Content, Name, Interest, Nack
from PiCN.Layers.TimeoutPreventionLayer import BasicTimeoutPreventionLayer, TimeoutPreventionMessageDict
from PiCN.ProgramLibs.Chat import ChatGUI


class Chat(object):
    def __init__(self, peer):
        self.peer = peer
        self.received_messages = []
        self.sent_messages = []

#methode send_message
#methode receive_message nimm vom sync layer entgegen und gibt aus
class Chatclient(object):
    """Chat for PiCN"""

    def __init__(self, ip: str, port: int, log_level=255, encoder: BasicEncoder = None, autoconfig: bool = False,
                 interfaces=None):
        self.chat_dict = {}
        # create encoder and chunkifyer
        if encoder is None:
            self.encoder = SimpleStringEncoder(log_level=log_level)
        else:
            encoder.set_log_level(log_level)
            self.encoder = encoder
        self.chunkifyer = SimpleContentChunkifyer()

        # initialize layers
        synced_data_struct_factory = PiCNSyncDataStructFactory()
        synced_data_struct_factory.register("faceidtable", FaceIDDict)
        synced_data_struct_factory.register("sync_dict", SynchronisationMessageDict)
        synced_data_struct_factory.create_manager()
        faceidtable = synced_data_struct_factory.manager.faceidtable()
        # timeoutprevention_dict = synced_data_struct_factory.manager.timeoutprevention_dict()
        sync_dict = synced_data_struct_factory.manager.sync_dict()
        self.GUI = ChatGUI(self)

        if interfaces is None:
            interfaces = [UDP4Interface(0)]
        else:
            interfaces = interfaces

        # create layers
        self.linklayer = BasicLinkLayer(interfaces, faceidtable, log_level=log_level)
        self.packetencodinglayer = BasicPacketEncodingLayer(self.encoder, log_level=log_level)
        self.chunklayer = BasicChunkLayer(self.chunkifyer, log_level=log_level)
        self.synchronisationLayer = BasicSynchronisationLayer(sync_dict, None, log_level=log_level)
        self.lstack: LayerStack = LayerStack([
            self.synchronisationLayer,
            self.chunklayer,
            self.packetencodinglayer,
            self.linklayer
        ])
        self.autoconfig = autoconfig
        if autoconfig:
            self.autoconfiglayer: AutoconfigClientLayer = AutoconfigClientLayer(self.linklayer)
            self.lstack.insert(self.autoconfiglayer, on_top_of=self.packetencodinglayer)

        # setup communication
        if port is None:
            self.fid = self.linklayer.faceidtable.get_or_create_faceid(AddressInfo(ip, 0))
        else:
            self.fid = self.linklayer.faceidtable.get_or_create_faceid(AddressInfo((ip, port), 0))
        self.synchronisationLayer.new_messages_loop(self.fid)

        #todo make log stuff with ibf

        # send packet
        self.lstack.start_all()

    def start_chat(self, peer, name: Name, timeout=4.0) -> str:
        """Fetch data from the server
        :param peer Peer with which Chat is to be initiated
        :param name Name to be fetched
        :param timeout Timeout to wait for a response. Use 0 for infinity
        """
        self.chat_dict[peer] = Chat(peer)
        #start a chat GUI
        #TODO ModuleNotFoundError: No module named 'tkinter' only works with Python 3.9
        #self.GUI = ChatGUI.ChatGUI(self, self.peer)
        # create interest
        interest: Interest = Interest(name)

        if self.autoconfig:
            self.lstack.queue_from_higher.put([None, interest])
        else:
            # while True:
            self.lstack.queue_from_higher.put([self.fid, interest])
            # packet = self.lstack.queue_to_higher.get()[1]
            # print(packet.content)

        if timeout == 0:
            packet = self.lstack.queue_to_higher.get()[1]
        else:
            packet = self.lstack.queue_to_higher.get(timeout=timeout)[1]
        if isinstance(packet, Content):
            return packet.content
        if isinstance(packet, Nack):
            return "Received Nack: " + str(packet.reason.value)
        return None
    #aus nachricht interest und in queue_to_lower (to sync layer)
    def send_message(self, name, text):
        content: Content = Content(name, text)
        #interest: Interest = Interest(peer)
        if self.autoconfig:
            self.lstack.queue_from_higher.put([None, content])
        else:
            # while True:
            self.lstack.queue_from_higher.put([self.fid, content])
        #self.lstack.queue_from_higher.put([None, content])

        return
    #not necessary as for shared log?
    def receive_message(self):
        return

    def get_log(self):
        return self.chat_dict

    def stop_chat(self):
        """Close everything"""
        self.lstack.stop_all()
        self.lstack.close_all()

    #ageing in BasicICN für interest loop logic  try except finally
    #(setDeamon sagt Thread abhängig vom parent, wenn parent closed, thread auch closed)