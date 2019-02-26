from struct import *


class TCP_HEADER:
    def __init__(self, src_port=0, dst_port=0, sequence_num=0, ack_num=0, offset_reserved_ns=0, flags=0, window_size=0, checksum=0):
        self.src_port = src_port
        self.dst_port = dst_port
        self.sequence_num = sequence_num
        self.ack_num = ack_num
        self.offset_reserved_ns = offset_reserved_ns
        self.flags = flags
        self.window_size = window_size
        self.checksum = checksum
        self.packed_header = bytearray()
        self.pack()

    def pack(self):
        self.packed_header = Struct('!HH I I BBH HH').pack(self.src_port, self.dst_port,\
                                                           self.sequence_num, self.ack_num,\
                                                           self.offset_reserved_ns, self.flags,\
                                                           self.window_size, self.checksum, 0)

    def parse(self, raw_packet):
        self.src_port, self.dst_port, \
        self.sequence_num, self.ack_num, \
        self.offset_reserved_ns, self.flags, \
        self.window_size, self.checksum, urgent_pointer = Struct('!HH I I BBH HH').unpack_from(raw_packet, 0)

    def log(self):
        print("########TCP Header########\nsrc port:", self.src_port,\
              "\ndest port:", self.dst_port,\
              "\nseq. num:", self.sequence_num,\
              "\nack num:", self.ack_num,\
              "\noffset reserved NS:", self.offset_reserved_ns, self.flags,\
              "\nwindow size:", self.window_size,\
              "\nchecksum:", self.checksum)