from PiCN.ProgramLibs.Fetch import Fetch
from PiCN.ProgramLibs.Chat import Chatclient
from PiCN.ProgramLibs.NFNForwarder import NFNForwarder
from PiCN.ProgramLibs.ICNForwarder import ICNForwarder
from PiCN.Layers.LinkLayer.Interfaces import SimulationBus
from PiCN.Layers.LinkLayer.Interfaces import AddressInfo
from PiCN.Layers.PacketEncodingLayer.Encoder import BasicEncoder, SimpleStringEncoder, NdnTlvEncoder
from PiCN.Mgmt import MgmtClient
from PiCN.Packets import Content, Interest, Name
import concurrent.futures
import threading
from PiCN.Layers.SynchronisationLayer.BloomFilters.InvertibleBloomFilter import InvertibleBloomFilter

ifb = InvertibleBloomFilter(10)
ifb.insert_element(5, 'DiegDeil')
simulation_bus = SimulationBus(packetencoder=NdnTlvEncoder())
icn_fwd0 = ICNForwarder(port=0, encoder=NdnTlvEncoder(), interfaces=[simulation_bus.add_interface("icn0")],
                        log_level=0, ageing_interval=1)
icn_fwd1 = ICNForwarder(port=0, encoder=NdnTlvEncoder(), interfaces=[simulation_bus.add_interface("icn1")],
                        log_level=0, ageing_interval=1)
mgmt_client0 = MgmtClient(icn_fwd0.mgmt.mgmt_sock.getsockname()[1])
mgmt_client1 = MgmtClient(icn_fwd1.mgmt.mgmt_sock.getsockname()[1])


chat_tool0 = Chatclient("icn0", None, 0, NdnTlvEncoder(), interfaces=[simulation_bus.add_interface("chattool0")])
chat_tool1 = Chatclient("icn1", None, 0, NdnTlvEncoder(), interfaces=[simulation_bus.add_interface("chattool1")])

icn_fwd0.start_forwarder()
icn_fwd1.start_forwarder()
simulation_bus.start_process()

#icn0 mit icn1 verbunden
# Chattool0 <-- ICN0 <--> ICN1 --> Chattool1

# mgmt_client0.add_face("icn1", None, 0)
# mgmt_client0.add_forwarding_rule(Name("/data"), [1])
#
# mgmt_client0.add_face("icn0", None, 0)
# mgmt_client0.add_forwarding_rule(Name("/chattool1"), [0])
#
# mgmt_client1.add_face("icn1", None, 1)
# mgmt_client1.add_forwarding_rule(Name("/chattool0"), [0])
#
# mgmt_client0.add_face('chattool0', None, 0)
# mgmt_client0.add_forwarding_rule(Name("/chattool0"), [1])
#
# mgmt_client1.add_face("chattool1", None, 0)
# mgmt_client1.add_forwarding_rule(Name("/chattool1"), [1])
#
mgmt_client0.add_face("icn1", None, 0)
mgmt_client0.add_forwarding_rule(Name("/chattool1"), [0])

mgmt_client1.add_face("icn0", None, 0)
mgmt_client1.add_forwarding_rule(Name("/chattool0"), [0])

mgmt_client0.add_face('chattool0', None, 0)
mgmt_client0.add_forwarding_rule(Name("/chattool0"), [1])

mgmt_client1.add_face("chattool1", None, 0)
mgmt_client1.add_forwarding_rule(Name("/chattool1"), [1])

mgmt_client0.add_new_content(Name("/data/message_sync"), "Ping")
mgmt_client1.add_new_content(Name("/data/message_sync"), "Pong")
#name0 = Name("/data/obj1")
#name1 = Name("/data/obj1")

#chat_tool0.send_message(Name("/data/obj1"), "Hello World")

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     future = executor.submit(chat_tool0.start_chat, 1, name0, timeout=20)
#     res0 = future.result()
#     print(res0)



# with concurrent.futures.ThreadPoolExecutor() as executor:
#     future = executor.submit(chat_tool1.start_chat, 1, name1, timeout=20)
#     res1 = future.result()
#     print(res1)


icn_fwd0.stop_forwarder()
icn_fwd1.stop_forwarder()
chat_tool0.stop_chat()
simulation_bus.stop_process()
mgmt_client0.shutdown()
mgmt_client1.shutdown()
