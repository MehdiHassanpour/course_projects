from math import floor
from random import uniform

from TCP_Header import *


class TCP_PACKET:
    def __init__(self, raw_packet=bytearray(), payload=bytearray()):
        self.packed_packet = raw_packet
        self.header = TCP_HEADER()
        self.payload = payload
        self.isValid = False
        self.checksum = 0
        if len(raw_packet):
            self.header.parse(raw_packet)
            if not len(payload) and len(raw_packet) > 20:
                self.payload = Struct("%ds" % (len(raw_packet)-20)).unpack_from(raw_packet, 20)[0]
                self.packed_packet += self.payload
            elif len(payload) != 0:
                self.packed_packet += payload
            checksum_tmp = self.header.checksum
            self.header.checksum = 0
            self.pack()
            self.calculate_checksum()
            if self.checksum == checksum_tmp:
                self.isValid = True
            else:
                self.isValid = False
            self.header.checksum = checksum_tmp
            self.pack()

    def create_packet(self, src_port=0, dst_port=0, sequence_num=0, ack_num=0, offset_reserved_ns=0, flags=0, window_size=0, payload=bytearray()):
        self.header = TCP_HEADER(src_port, dst_port, sequence_num, ack_num, offset_reserved_ns, flags, window_size, 0)
        self.payload = payload
        # self.header.pack()
        self.packed_packet = self.header.packed_header + payload
        self.calculate_checksum()
        self.header.checksum = self.checksum
        self.isValid = True
        self.pack()

    def calculate_checksum(self):
        raw_packet_copy = self.packed_packet
        checksum = 0
        # print("DEBUG-- calculate_checksum: len: ", len(raw_packet_copy), "packet: ", raw_packet_copy)
        if not len(raw_packet_copy) % 2 == 0:
            raw_packet_copy += Struct('!B').pack(0)
        for halfword_num in range(0, len(raw_packet_copy), 2):
            # byte1, raw_packet_copy = Struct('!B%ds' % (len(raw_packet_copy)-1)).unpack(raw_packet_copy)
            # byte2, raw_packet_copy = Struct('!B%ds' % (len(raw_packet_copy)-1)).unpack(raw_packet_copy)
            # halfword = byte1 + (byte2 << 8)
            # checksum_tmp = checksum + halfword
            # checksum = ~((checksum_tmp & 0xffff) + (checksum_tmp >> 16)) & 0xffff
            # halfword = ord(raw_packet_copy[halfword_num*8:(halfword_num+1)*8]) + \
            #            (ord(raw_packet_copy[(halfword_num+1)*8:(halfword_num+2)*8]) << 8)
            halfword = (raw_packet_copy[halfword_num]) + (raw_packet_copy[halfword_num+1] << 8)
            # print(raw_packet_copy[halfword_num], (raw_packet_copy[halfword_num+1], halfword))
            checksum_tmp = checksum + halfword
            checksum = ~((checksum_tmp & 0xffff) + (checksum_tmp >> 16)) & 0xffff
            # checksum = (~(checksum + (checksum >> 16)) & 0xffff)
        # print("DEBUG-- calculate_checksum: ", checksum)
        self.checksum = checksum

    def pack(self):
        self.header.pack()
        if len(self.payload) == 0:
            self.packed_packet = self.header.packed_header
        else:
            self.packed_packet = self.header.packed_header + self.payload

    def log(self):
        print("#####TCP Packet#######\npayload: ", str(self.payload, 'Latin-1'), "\nchecksum:", self.checksum)
        self.header.log()


def create_syn(sender_port, receiver_port):
    syn_packet = TCP_PACKET()
    syn_packet.create_packet(src_port=sender_port, dst_port=receiver_port, \
                             sequence_num=int(floor(uniform(0, (2 ** 32) - 1))),\
                             ack_num=0, offset_reserved_ns=0x50, flags=0x02, window_size=1)
    return syn_packet


def create_ack(sender_port, receiver_port, sequence_num, ack_num):
    ack_packet = TCP_PACKET()
    ack_packet.create_packet(src_port=sender_port, dst_port=receiver_port, \
                             sequence_num=sequence_num, \
                             ack_num=ack_num, offset_reserved_ns=0x50, flags=0x10, window_size=1)
    return ack_packet


def create_syn_ack(sender_port, receiver_port, sequence_num, ack_num):
    syn_ack_packet = TCP_PACKET()
    syn_ack_packet.create_packet(src_port=sender_port, dst_port=receiver_port, \
                             sequence_num=sequence_num, \
                             ack_num=ack_num, offset_reserved_ns=0x50, flags=0x12, window_size=1)
    return syn_ack_packet


def receive_packet(read_file):
    # file = open(read_path, 'rb', 0)
    file = read_file
    while True:
        size_in_byte = file.read(4)
        if len(size_in_byte) == 0:
            continue
        else:
            # print("DEBUG-- receive_packet size: ", size_in_byte)
            size = Struct('!I').unpack(size_in_byte)[0]
            data = file.read(size)
            # print("DEBUG-- receive_packet data: ", data)
            raw_packet = Struct('!%ds' % size).unpack(data)[0]
            packet = TCP_PACKET(raw_packet=raw_packet)
            if not packet.isValid:
                # print("DEBUG-- PACKET CHECKSUM IS NOT VALID, header.checksum:", packet.header.checksum)
                continue
            else:
                return packet


def send_packet(write_file, raw_packet):
    file = write_file
    size = len(raw_packet)
    # file = open(write_path, 'wb', 0)
    file.write(Struct('!I').pack(size))
    file.flush()
    file.write(raw_packet)
    # file.write(Struct('!%ds' % size).pack(size, raw_packet))
    # file.write(raw_packet)
    file.flush()
    # file.close()
