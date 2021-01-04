import multiprocessing
import time
from typing import Dict, List

from PiCN.Layers.ChunkLayer.Chunkifyer import BaseChunkifyer, SimpleContentChunkifyer
from PiCN.Packets import Content, Interest, Name, Nack
from PiCN.Processes import LayerProcess
from PiCN.Layers.ICNLayer.PendingInterestTable import BasePendingInterestTable


class SynchronisationMessageDict(object):
    def __init__(self):
        self.container: Dict[Name, SynchronisationMessageDict.SynchronisationMessageDictEntry] = {}

class BasicTimeoutPreventionLayer(LayerProcess):

    def __init__(self, message_dict: SynchronisationMessageDict,
                 pit: BasePendingInterestTable = None, log_level=255):
        super().__init__("Sync", log_level)

    def data_from_higher(self, to_lower: multiprocessing.Queue, to_higher: multiprocessing.Queue, data):
        packet_id = data[0]
        packet = data[1]
        if isinstance(packet, Interest):
            return
        if isinstance(packet, Content):
            return
        if isinstance(packet, Nack):
            return
    def data_from_lower(self, to_lower: multiprocessing.Queue, to_higher: multiprocessing.Queue, data):
        packet_id = data[0]
        packet = data[1]
        if isinstance(packet, Interest):
            return
        if isinstance(packet, Content):
            return
        if isinstance(packet, Nack):
            return
