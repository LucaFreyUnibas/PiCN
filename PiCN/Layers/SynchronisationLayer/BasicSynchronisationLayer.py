import multiprocessing
import time, threading
from typing import Dict, List

from PiCN.Layers.ChunkLayer.Chunkifyer import BaseChunkifyer, SimpleContentChunkifyer
from PiCN.ProgramLibs.Chat import Chatclient
from PiCN.Packets import Content, Interest, Name, Nack
from PiCN.Processes import LayerProcess
from PiCN.Layers.ICNLayer.ForwardingInformationBase import BaseForwardingInformationBase, ForwardingInformationBaseEntry
from PiCN.Layers.RoutingLayer.RoutingInformationBase import BaseRoutingInformationBase
from PiCN.Layers.ICNLayer.PendingInterestTable import BasePendingInterestTable
from PiCN.Layers.SynchronisationLayer.BloomFilters.InvertibleBloomFilter import InvertibleBloomFilter

#Chatdictionary hier
class SynchronisationMessageDict(object):
    def __init__(self, pit: BasePendingInterestTable=None, fib=BaseForwardingInformationBase):
        self.container: Dict[Name, SynchronisationMessageDict.SynchronisationMessageDictEntry] = {}
        self.ibf = InvertibleBloomFilter(100)
        #self.pit = pit
        #self.fib = fib
    class SynchronisationMessageDictEntry(object):
        """Datastructure Entry"""

        def __init__(self, packetid):
            self.last_msg_id = None
            self.timestamp = time.time()
            self.packet_id = packetid
            self.chat_id = None

    def get_entry(self, name: Name) -> SynchronisationMessageDictEntry:
        """search for an entry in the Dict
        :param name: name of the entry
        :return entry if found, else None
        """
        if name in self.container:
            return self.container.get(name)

    def add_entry(self, chat_id: Name, entry: SynchronisationMessageDictEntry):
        """add an entry to the dict
        :param name: Name of the Entry
        :param entry: the entry itself
        """
        self.container[chat_id] = entry

    def create_entry(self, packet_id, chat_id: Name):
        """create an new entry given a name
        :param name: name for the entry
        """
        entry = SynchronisationMessageDict.SynchronisationMessageDictEntry(packet_id)
        self.add_entry(chat_id, entry)

    def update_timestamp(self, name: Name):
        """set the timestamp of the corresponding entry to time.time()
        :param name: Name of the Entry to be updated
        """
        entry = self.container.get(name)
        if entry is not None:
            self.remove_entry(name)
        else:
            return
        entry_n = SynchronisationMessageDict.SynchronisationMessageDictEntry(entry.packetid)
        self.add_entry(name, entry_n)

    def remove_entry(self, name):
        """Remove an entry from the dict
        :param name: name of the entry to be removed
        """
        if name in self.container:
            del self.container[name]

    def get_container(self):
        return self.container


class BasicSynchronisationLayer(LayerProcess):

    def __init__(self, message_dict: SynchronisationMessageDict,
                 pit: BasePendingInterestTable = None, log_level=255):
        super().__init__("Sync", log_level)
    #Requests
        self.message_dict = message_dict
        self.loop_interval = 2
    #meesage sync loop, ask other client for its IBF
    def new_messages_loop(self, fid):
        # last_msg_id = self.message_dict.get_entry(peer).last_msg_id
        # interest: Interest = Interest("/message_sync/" + peer + "/" + last_msg_id)

        #timestamp = time.time()
        try:
            interest: Interest = Interest(Name("/data/message_sync"))
            self.queue_to_lower.put([fid, interest])
        except Exception as e:
            print(e)
            self.logger.warning("Exception during Sync Loop")
            return
        t = threading.Timer(self.loop_interval, self.new_messages_loop, args=[fid])
        t.setDaemon(True)
        t.start()
    #data from higer is always a new message from the Chatclient whichh must be put into the dict
    def data_from_higher(self, to_lower: multiprocessing.Queue, to_higher: multiprocessing.Queue, data):
        print(str(data[1].content))
        packet_id = data[0] #was face_id
        packet = data[1]
        if isinstance(packet, Interest):
            self.handle_interest_from_higher(packet_id, packet) #was face_id
            return
        if isinstance(packet, Content):
            print(str(data[1].content))
            # todo save msg to log(calss with seqnum,msg and ibf) , packet.content
            if self.message_dict.get_entry(packet.name) is None:
                self.message_dict.create_entry(packet_id=packet_id, chat_id=packet.name)
            to_lower.put([packet_id, packet])
            return
        if isinstance(packet, Nack):
            return
    #PSync data arrives from lower therefore its communication with the other client
    def data_from_lower(self, to_lower: multiprocessing.Queue, to_higher: multiprocessing.Queue, data):
        face_id = data[0]
        packet = data[1]
        #Interests are either Sync Interests or asking for a specific data name
        if isinstance(packet, Interest):
            self.handle_interest_from_lower(face_id, packet)

            return
        #either the latest IBF from our chatpartner or new data names
        if isinstance(packet, Content):
            print("this is content:", packet.content)
            self.message_dict.add_entry(Content.content.split("/")[0], Content.content.split("/")[1])
            Chatclient.receive_message()
            return
        if isinstance(packet, Nack):
            return
    #probably not necessary
    def handle_interest_from_higher(self, face_id: int, interest: Interest, to_lower: multiprocessing.Queue,
                                    to_higher: multiprocessing.Queue):

        return

    def handle_interest_from_lower(self, face_id: int, interest: Interest, to_lower: multiprocessing.Queue,
                                   to_higher: multiprocessing.Queue, from_local: bool = False):
        if self.message_dict.get_entry(interest.name) is not None:
            if self.message_dict.get_entry(interest.name).last_msg_id < interest.name.split("/", 1):
                message_from = self.message_dict(interest.name)
                content: Content = Content(message_from, self.message_dict(interest.name))
                to_lower.put[face_id, content]
        return

    def ageing(self):
        return
