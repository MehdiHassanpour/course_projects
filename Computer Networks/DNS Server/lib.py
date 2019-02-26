from struct import Struct
from socket import inet_ntoa

packet_header_struct = Struct('!HBBHHHH')


class DNS_PACKET_HEADER:
    def __init__(self, data):
        self.message_id = data[0]
        self.qr_to_rd = data[1] #QR; OPCODE:4; AA; TC; RD; RA
        self.ra_to_rcode = data[2]
        self.QDCOUNT = data[3]
        self.ANCOUNT = data[4]
        self.NSCOUNT = data[5]
        self.ARCOUNT = data[6]

    def printAll(self):
        print("###########DEBUG--Header############")
        print(self.message_id)
        print(self.qr_to_rd, self.ra_to_rcode)
        print(self.QDCOUNT) # question no
        print(self.ANCOUNT) # answer no
        print(self.NSCOUNT) # authority no
        print(self.ARCOUNT) # additional no
        print("#######################")


class DNS_PACKET_QUESTION:
    class QNAME:
        def __init__(self, len = 0, domain_name=""):
            self.len = len
            self.domain_name = domain_name

    def __init__(self, qtype=0, qclass=0):
        self.qnames = []
        self.QTYPE = qtype
        self.QCLASS = qclass

    def printAll(self):
        print("###########DEBUG--Question############")
        for i in self.qnames:
            print(i.len, i.domain_name)
        print(self.QTYPE)
        print(self.QCLASS)
        print("#######################")


class DNS_PACKET_ANSWER:
    class ANAME:
        def __init__(self, len = 0, domain_name=""):
            self.len = len
            self.domain_name = domain_name

    def __init__(self, atype=0, aclass=0, ttl=0, rdlength=0, rdata=""):
        self.names = []
        self.ATYPE = atype
        self.ACLASS = aclass
        self.ttl = ttl
        self.RDLength = rdlength
        self.rdata = rdata

    def printAll(self):
        print("###########DEBUG--Answer############")
        for i in self.names:
            print(i.len, i.domain_name)
        print(self.ATYPE)
        print(self.ACLASS)
        print(self.ttl)
        print(self.RDLength)
        print(self.rdata)
        print("#######################")


def find_name_in_packet(raw_packet, processing_packet):
    bytes_read = 0
    unpack_ptr = 0
    name = ""
    is_pointer = False
    packet_to_parse_for_names = processing_packet
    name_len = Struct('!B').unpack_from(packet_to_parse_for_names, unpack_ptr)[0]
    if (name_len & 0b11000000) == 0b11000000:  # raw_packet pointer
        is_pointer = True
        unpack_ptr = ((Struct('!H').unpack_from(packet_to_parse_for_names, unpack_ptr)[0]) & 16383)
        bytes_read += 2
        packet_to_parse_for_names = raw_packet
        name_len = Struct('!B').unpack_from(packet_to_parse_for_names, unpack_ptr)[0]
        unpack_ptr += 1
    else:
        bytes_read += 1
        unpack_ptr += 1
    while name_len != 0:
        name += str(Struct('!%ds' % name_len).unpack_from(packet_to_parse_for_names, unpack_ptr)[0], 'utf-8')
        # print(name)
        unpack_ptr += name_len
        if not is_pointer:
            bytes_read = unpack_ptr
        name_len = Struct('!B').unpack_from(packet_to_parse_for_names, unpack_ptr)[0]
        if (name_len & 0b11000000) == 0b11000000:  # checking for pointer
            is_pointer = True
            name += "."

            # print("debug--lib--", Struct('!H').unpack_from(packet_to_parse_for_names, unpack_ptr)[0], "\n", unpack_ptr)
            unpack_ptr = (Struct('!H').unpack_from(packet_to_parse_for_names, unpack_ptr)[0] & 16383)
            packet_to_parse_for_names = raw_packet
            # print("debug-- lib--", packet_to_parse_for_names, "\n", unpack_ptr, "\n", processing_packet)
            name_len = Struct('!B').unpack_from(packet_to_parse_for_names, unpack_ptr)[0]
            unpack_ptr += 1
        else:
            unpack_ptr += 1
            if name_len != 0:
                name += "."
    if not is_pointer:
        bytes_read = unpack_ptr
    return name, bytes_read


class LOG:
    def __init__(self, file_name=""):
        self.file_name = file_name

    def print_str(self, str):
        file = open(self.file_name+".txt", 'a')
        file.write(str)
        file.close()

    def connect_to_ip(self, ip):
        splited_ip = ip.split('.')
        file = open(self.file_name+".txt", 'a')
        file.write("connecting to ")
        for i in range(len(splited_ip)):
            file.write(splited_ip[i])
            if i != (len(splited_ip)-1):
                file.write('.')
        file.write('\n===============\n')
        file.close()

    def print_header(self, header):
        file = open(self.file_name+".txt", 'a')
        file.write("HEADER\n===============\n{\n")
        file.write("additional count : " + str(header.ARCOUNT) + "\n")
        file.write("answer count : " + str(header.ANCOUNT) + "\n")
        file.write("authority count : " + str(header.NSCOUNT) + "\n")
        file.write("id : " + str(header.message_id) + "\n" + "is authoritative : " + str(bool(header.qr_to_rd & 0b00000100)) + "\n")
        file.write("is response : " + str(bool(header.qr_to_rd & 0b10000000)) + "\n")
        file.write("is truncated : " + str(bool(header.qr_to_rd & 0b00000010)) + "\n")
        file.write("opcode : " + str((header.qr_to_rd & 0b01111000) >> 3) + "\nquestion count : " + str(header.QDCOUNT) + "\nrecursion available : " + str(bool(header.ra_to_rcode & 0b10000000)) + "\n")
        response_code = "No Error"
        if(header.ra_to_rcode & 0b00001111) == 1:
            response_code = "Format Error"
        elif(header.ra_to_rcode & 0b00001111) == 2:
            response_code = "Server Failure"
        elif(header.ra_to_rcode & 0b00001111) == 3:
            response_code = "Format Name Error"
        elif(header.ra_to_rcode & 0b00001111) == 4:
            response_code = "Not Implemented"
        elif(header.ra_to_rcode & 0b00001111) == 5:
            response_code = "Refused"
        else:
            response_code = "No Error"
        file.write("recursion desired : " + str(bool(header.qr_to_rd & 0b00000001)) + "\n" + "reserved : " + str((header.ra_to_rcode & 0b01110000) >> 4) + "\nresponse code : " + response_code + "\n}\n")
        file.write('===============\n')
        file.close()

    def print_question(self, question):
        file = open(self.file_name + ".txt", 'a')
        file.write("QUESTION\n===============\n{\n")
        file.write("Domain Name : ")
        for i in range(len(question.qnames)):
            file.write(str(question.qnames[i].domain_name, 'utf-8'))
            if i != (len(question.qnames)-1):
                file.write(".")

        file.write("\nQuery Class : " + str(question.QCLASS) + "\nQuery Type : " + str(question.QTYPE) + "\n}\n")
        file.write('===============\n')
        file.close()

    def print_answer_packet(self, answer, raw_packet):
        file = open(self.file_name+".txt", 'a')
        file.write("{\nclass : " + str(answer.ACLASS) + "\nname : ")
        for i in range(len(answer.names)):
            file.write(str(answer.names[i].domain_name, 'utf-8'))
            if i != (len(answer.names)-1):
                file.write(".")
        rdata = ""
        type = str(answer.ATYPE)
        if answer.ATYPE == 1: # A
            type = "A"
            str_ip = inet_ntoa(answer.rdata)
            splited_ip = str_ip.split('.')
            rdata = splited_ip[0] + "." + splited_ip[1] + "." + splited_ip[2] + "." + splited_ip[3]
        elif answer.ATYPE == 2: # NS
            type = "NS"
            rdata, tmp = find_name_in_packet(raw_packet, answer.rdata)
        elif answer.ATYPE == 5: # CNAME
            rdata, tmp = find_name_in_packet(raw_packet, answer.rdata)
        elif answer.ATYPE == 6: # SOA
            type = "SOA"
            primary_ns, bytes_read = find_name_in_packet(raw_packet, answer.rdata)
            processing_packet = Struct('!%ds%ds' % (bytes_read, answer.RDLength - bytes_read)).unpack(answer.rdata)[1]
            admin_mb, bytes_read = find_name_in_packet(raw_packet, processing_packet)
            serial_num, refresh_interval, retry_interval, expiration_limit, min_ttl = Struct('!IIIII').unpack_from(processing_packet, bytes_read)
            rdata = "\n{\nAdmin MB : " + admin_mb + "\nExpiration Limit : " + str(expiration_limit) + "\nMinimum TTL : " + str(min_ttl) + "\nPrimary NS : " + primary_ns + "\nRefresh interval : " + str(refresh_interval) + "\nRetry interval : " + str(retry_interval) + "\nSerial Number : " + str(serial_num) + "\n}"
        elif answer.ATYPE == 12: # PTR
            type = "PTR"
            rdata, tmp = find_name_in_packet(raw_packet, answer.rdata)
        elif answer.ATYPE == 15: # MX
            type = "MX"
            preference , processing_packet = Struct('!H %ds' % (answer.RDLength - 2)).unpack(answer.rdata)
            name, tmp = find_name_in_packet(raw_packet, processing_packet)
            rdata = "\n{\n‫‪Mail‬‬ ‫‪Exchanger‬ : " + name + "\n‬‫‪Preference‬‬ ‫‪:‬" + str(tmp) + "\n}"
        elif answer.ATYPE == 16:
            type = "TXT"
            rdata = str(answer.rdata, 'utf-8')
        elif answer.ATYPE == 28: # AAAA
            type = "AAAA"
            ipv6 = []
            for i in range(8):
                tmp = Struct('!H').unpack_from(answer.rdata, i*2)[0]
                rdata += ("0x%0.4x" % tmp)[2:]
                if i != 7:
                    rdata += ":"
        else:
            pass
        # TODO: TXT rdata format; AAAA
        file.write("\nrdata : " + rdata + "\nrdlength : " + str(answer.RDLength) + "\nttl : " + str(answer.ttl) + "\ntype : " + type + "\n}\n")
        file.close()
