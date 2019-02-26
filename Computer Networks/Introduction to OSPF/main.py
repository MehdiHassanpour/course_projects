import dpkt
# import socket
from struct import Struct
from library import *
import sys


adjacent_matrix = {}
packets_file_name = str(sys.argv[1])  # "Packets.pcap"
packets_file = open(packets_file_name, 'rb')

for time, packet in dpkt.pcap.Reader(packets_file):
    # print time, packet
    eth = dpkt.ethernet.Ethernet(packet)
    # print type(eth.data)
    if type(eth.data) == dpkt.ip.IP:
        # print type(eth.data.data)
        if type(eth.data.data) == dpkt.ospf.OSPF:
            # print type(eth.data.data)
            ospf = eth.data.data
            if ospf.type == 4: # LS Update
                # ospf.data
                lsa_num, ospf_packet = Struct('!I %ds' % (len(ospf.data) - 4)).unpack_from(ospf.data, 0)
                ospf_packet_offset = 0
                for i in range(lsa_num):
                    # handle_lsup(ospf_packet)
                    lsu_header = LSU_HEADER()
                    ospf_packet_offset_tmp = lsu_header.parse(ospf_packet, ospf_packet_offset)
                    if lsu_header.type == 1:  # Router-LSA
                        # lsu_header.log()
                        flags, temp, links_num = Struct('!B B H').unpack_from(ospf_packet, ospf_packet_offset_tmp)
                        ospf_packet_offset_tmp += 4
                        for j in range(links_num):
                            link = LINK()
                            ospf_packet_offset_tmp = link.parse(ospf_packet, ospf_packet_offset_tmp)
                            if link.type == 3:  # Stub
                                # print socket.inet_ntoa(Struct('!L').pack(link.id)), socket.inet_ntoa(Struct('!L').pack(lsu_header.id))
                                link_ip_str = link.id
                                lsu_ip_str = lsu_header.id
                                # link_ip_str = socket.inet_ntoa(Struct('!L').pack(link.id))
                                # lsu_ip_str = socket.inet_ntoa(Struct('!L').pack(lsu_header.id))
                                if lsu_ip_str in adjacent_matrix:
                                    adjacent_matrix[lsu_ip_str].append(link_ip_str)
                                else:
                                    adjacent_matrix[lsu_ip_str] = [link_ip_str]
                                # if link_ip_str in adjacent_matrix:
                                #     adjacent_matrix[link_ip_str].append(lsu_ip_str)
                                # else:
                                #     adjacent_matrix[link_ip_str] = [lsu_ip_str]
                    else:
                        pass
                    ospf_packet_offset += lsu_header.length
            else:
                pass
        else:
            continue
    else:
        continue


file = open("adjacent_matrix.txt",  'w')
routers_checked = []
routers = sorted(adjacent_matrix.keys())
data = 0
for router1 in routers:
    for router2 in routers:
        if router1 == router2:
            if router2 != routers[0]:
                file.write(",")
            file.write("0")
            continue
        for link in adjacent_matrix[router1]:
            if link in adjacent_matrix[router2]:
                # file.write(",1"
                data = 1
                break
            else:
                data = 0
                # file.write(",0")
        if router2 != routers[0]:
            file.write(",")
        file.write(str(data))
    if router1 != routers[-1]:
        file.write("\n")
file.close()

# for key in adjacent_matrix:
#     print key, ":", adjacent_matrix[key]
#     router = min(adjacent_matrix.keys())
#     routers_checked.append(router)
#     for item in adjacent_matrix[router]:
#         for key in adjacent_matrix:
#             if
#     # file.write("0,")
