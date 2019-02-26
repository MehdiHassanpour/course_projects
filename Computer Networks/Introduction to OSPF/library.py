from struct import *


class LSU_HEADER:
    def __init__(self, age=0, options=0, type=0, id=0,\
                 advertising_router=0, seqnum=0, checksum=0,\
                 length=0):
        self.age = age
        self.options = options
        self.type = type
        self.id = id
        self.advertising_router = advertising_router
        self.seqnum = seqnum
        self.checksum = checksum
        self.length = length

    def parse(self, raw_packet, offset):
        self.age, self.options, self.type, self.id,\
        self.advertising_router, self.seqnum, self.checksum,self.length\
            = Struct('!H B B I I I H H').unpack_from(raw_packet, offset)
        offset += 20
        return offset

    def log(self):
        print "############## LSU Header #############"
        print "age:", self.age, ", options:", self.options, ", type:", self.type
        print "id:", self.id, "\nadvertising router:", self.advertising_router
        print "sequence number: ", self.seqnum
        print "checksum:", self.checksum, ", length:", self.length
        print "#######################################"


class LINK:
    def __init__(self):
        self.id = 0
        self.data = 0
        self.type = 0
        self.metrics_num = 0
        self.metric = 1

    def parse(self, raw_packet, offset):
        self.id, self.data,  self.type, self.metrics_num,\
        self.metric = Struct('!I I B B H').unpack_from(raw_packet, offset)
        offset += 12
        return offset

    def log(self):
        print "############## LINK #############"
        print "id:", self.id
        print "data:", self.data
        print "type:", self.type, ", number of metrics:", self.metrics_num, ", metric:", self.metric