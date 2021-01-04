from PiCN.ProgramLibs.Fetch import Fetch
from PiCN.ProgramLibs.NFNForwarder import NFNForwarder
from PiCN.ProgramLibs.ICNForwarder import ICNForwarder
from PiCN.Layers.LinkLayer.Interfaces import SimulationBus
from PiCN.Layers.LinkLayer.Interfaces import AddressInfo
from PiCN.Layers.PacketEncodingLayer.Encoder import BasicEncoder, SimpleStringEncoder, NdnTlvEncoder
from PiCN.Mgmt import MgmtClient
from PiCN.Packets import Content, Interest, Name

simulation_bus = SimulationBus(packetencoder=NdnTlvEncoder())
icn_fwd0 = ICNForwarder(port=0, encoder=NdnTlvEncoder(), interfaces=[simulation_bus.add_interface("icn0")],
                        log_level=255, ageing_interval=1)
icn_fwd1 = ICNForwarder(port=0, encoder=NdnTlvEncoder(), interfaces=[simulation_bus.add_interface("icn1")],
                        log_level=255, ageing_interval=1)
mgmt_client0 = MgmtClient(icn_fwd0.mgmt.mgmt_sock.getsockname()[1])
mgmt_client1 = MgmtClient(icn_fwd1.mgmt.mgmt_sock.getsockname()[1])

fetch_tool = Fetch("icn0", None, 255, NdnTlvEncoder(), interfaces=[simulation_bus.add_interface("fetchtool1")])

icn_fwd0.start_forwarder()
icn_fwd1.start_forwarder()
simulation_bus.start_process()

mgmt_client0.add_face("icn1", None, 0)
mgmt_client0.add_forwarding_rule(Name("/data"), [0])

# mgmt_client0.add_new_content(Name("/data/obj2"), "PYTHON\nfunc\ndef func(a, b):\n    return a + b")
mgmt_client1.add_new_content(Name("/data/obj1"), "World")

name = Name("/data/obj1")
# name += '_("Hello",/data/obj1)'
# name += "ICN"

res = fetch_tool.fetch_data(name, timeout=20)
print(res)

icn_fwd0.stop_forwarder()
icn_fwd1.stop_forwarder()
fetch_tool.stop_fetch()
simulation_bus.stop_process()
mgmt_client0.shutdown()
mgmt_client1.shutdown()
