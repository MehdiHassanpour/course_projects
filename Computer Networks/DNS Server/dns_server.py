from socket import *
# import socket
import _thread

import binascii

from lib import *
import sys
import ctypes

IP = ''
PORT = 15353
# root_server_ip = '198.41.0.4'
root_server_ip = str(sys.argv[1])
file = None


def check_names(qnames, anames):
    if len(qnames) == len(anames):
        for qname, aname in zip(qnames, anames):
            # print(qname.domain_name, aname.domain_name)
            if qname.domain_name != aname.domain_name:
                return False
        return True
    else:
        return False


def parse_packet_answer(header, raw_packet, answer_packet, is_query):
    # print("DEBUG-- answer:", answer_packet, "is_query: ", is_query)
    bytes_read = 0
    unpack_ptr = 0
    is_pointer = False
    answers = []

    log = LOG(file_name=str(header.message_id))
    log.print_str("ANSWER\n===============\n")
    for i in range(header.ARCOUNT + header.ANCOUNT + header.NSCOUNT):
        if header.ANCOUNT == i:
            log.print_str("===============\nAUTHORITY\n===============\n")
        if header.NSCOUNT == i:
            log.print_str("===============\nADDITIONAL\n===============\n")
        unpack_ptr = bytes_read
        # print("DEBUG--", "answer", i, "unpacked_ptr: ", unpack_ptr)
        is_pointer = False
        answer = DNS_PACKET_ANSWER()
        data_to_parse_for_names = answer_packet
        name_len = Struct('!B').unpack_from(data_to_parse_for_names, unpack_ptr)[0]
        while (name_len & 0b11000000) == 0b11000000:  # raw_packet pointer
            unpack_ptr = ((Struct('!H').unpack_from(data_to_parse_for_names, unpack_ptr)[0]) & 16383)
            if not is_pointer:
                bytes_read += 2
            is_pointer = True
            data_to_parse_for_names = raw_packet
            name_len = Struct('!B').unpack_from(data_to_parse_for_names, unpack_ptr)[0]
        unpack_ptr += 1
        # else:
        #     bytes_read += 1
        #     unpack_ptr += 1
        # print("debug-- name_len: ", name_len)
        while name_len != 0:
            domain_name = Struct('!%ds' % name_len).unpack_from(data_to_parse_for_names, unpack_ptr)[0]
            unpack_ptr += name_len
            if not is_pointer:
                bytes_read = unpack_ptr
            aname = DNS_PACKET_ANSWER.ANAME(len=name_len, domain_name=domain_name)
            answer.names.append(aname)
            # print("DEBUG--", "adding name: ", aname.len, aname.domain_name)
            name_len = Struct('!B').unpack_from(data_to_parse_for_names, unpack_ptr)[0]
            # print("name_len", name_len)
            while (name_len & 0b11000000) == 0b11000000:  # 16383 = 0b0011111111111111; checking for pointer
                # print("pointer")
                is_pointer = True
                unpack_ptr = (Struct('!H').unpack_from(data_to_parse_for_names, unpack_ptr)[0] & 16383)
                data_to_parse_for_names = raw_packet
                name_len = Struct('!B').unpack_from(data_to_parse_for_names, unpack_ptr)[0]
            unpack_ptr += 1
                
        if not is_pointer:
            bytes_read = unpack_ptr
        # print("bytes_read: , unpackptr", bytes_read, unpack_ptr)
        answer.ATYPE = Struct('!H').unpack_from(answer_packet, bytes_read)[0]
        bytes_read += 2
        answer.ACLASS = Struct('!H').unpack_from(answer_packet, bytes_read)[0]
        bytes_read += 2
        answer.ttl = Struct('!L').unpack_from(answer_packet, bytes_read)[0]
        bytes_read += 4
        answer.RDLength = Struct('!H').unpack_from(answer_packet, bytes_read)[0]
        bytes_read += 2
        answer.rdata = Struct('!%ds' % answer.RDLength).unpack_from(answer_packet, bytes_read)[0]
        bytes_read += answer.RDLength
        log.print_answer_packet(answer, raw_packet)

        if answer.ATYPE == 1:  # answer type A
            answers.append(answer)
        if not is_query: # iQuery
            if answer.ATYPE == 2 or answer.ATYPE == 12:
                answers.append(answer)
        # answer.printAll()
    log.print_str("===============\n")
    return answers


def send_packet(packet, address, need_response):
    send_socket = socket(AF_INET, SOCK_DGRAM)
    send_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)    
    try:
        send_socket.sendto(packet, address)
        if need_response:
            data_rcv, addr = send_socket.recvfrom(1024)
            return data_rcv, addr
    except:
        pass# print("DEBUG--", "error sending packet")
    send_socket.close()


def send_refuse_packet(id, addr):
    # header.printAll()
    header = packet_header_struct.pack(id, 128, 5, 0, 0, 0, 0)
    # print("DEBUG-- packet to send in hex:", binascii.hexlify(header))
    send_packet(header, addr, 0)


def create_ask_root_packet(header, question):
    packet = packet_header_struct.pack(header.message_id, 1, 0, 1, 0, 0, 0) # + Struct('!B%dsHH' % (question.QNAME.len)).pack(question.QNAME.len, question.QNAME.domain_name, 255, 1)
    for qname in question.qnames:
        packet += Struct('!B%ds' % qname.len).pack(qname.len, qname.domain_name)
    packet += Struct('!BHH').pack(0, 255, 1)
    return packet


def create_answer_packet(header, answer, is_query, dns_name):
    packet = packet_header_struct.pack(header.message_id, 0b10000000, 0b00000000, 0, 1, 0, 0)
    for name in answer.names:
        packet += Struct('!B %ds' % name.len).pack(name.len, name.domain_name)
    if is_query:
        packet += Struct('!BHHIHI').pack(0, answer.ATYPE, 1, 3600, answer.RDLength, Struct('!I').unpack(answer.rdata)[0])
    else:
        packet += Struct('!BHHIH').pack(0, answer.ATYPE, 1, 3600, answer.RDLength)
        # print("debug-- create_answer_packet", dns_name)
        split_dns_name = dns_name.split('.')
        for i in range(len(split_dns_name)):
            packet += Struct("!B%ds" % len(split_dns_name[i])).pack(len(split_dns_name[i]), split_dns_name[i].encode('utf-8'))
        packet += Struct('!B').pack(0)
    return packet


def create_refuse_packet(id):
    header = packet_header_struct.pack(id, 128, 5, 0, 0, 0, 0)
    # print("DEBUG-- packet to send in hex:", binascii.hexlify(header))
    return header


def parse_packet_header(packed_header, addr):
    unpacked_header = packet_header_struct.unpack(packed_header)
    # print("DEBUG--", "header: ", unpacked_header)
    header = DNS_PACKET_HEADER(unpacked_header)
    # header.printAll()
    if (header.qr_to_rd >= 16) and (header.QDCOUNT > 0) and (header.ANCOUNT == 0) and (header.NSCOUNT == 0) and (header.ARCOUNT == 0):  # {QR, OPCODE} != 0
        # print("DEBUG--", "refused")
        send_refuse_packet(header.message_id, addr)
        return None, -1
    else:
        return header, 0


def parse_packet_question(header, data):
    question = DNS_PACKET_QUESTION()
    qname = question.QNAME()
    qname.len, rest_of_data = Struct('!B %ds' % (len(data)-1)).unpack(data)
    is_query = False
    while qname.len != 0:
        qname.domain_name, rest_of_data = Struct('!%ds%ds' % (qname.len, len(rest_of_data)-qname.len)).unpack(rest_of_data)
        if "www" not in str(qname.domain_name, "utf-8").lower():
            qname.domain_name = str(qname.domain_name, "utf-8").split('//')[-1].encode("utf-8")
            qname.len = len(qname.domain_name)
            question.qnames.append(qname)
            if not qname.domain_name.isdigit():
                if(str(qname.domain_name, 'utf-8') != "in-addr") and (str(qname.domain_name, 'utf-8') != "arpa"):
                    is_query = True
                # print("is_query true: ", qname.domain_name)
        # print("parse_question-- added", qname.len, qname.domain_name)
        qname = question.QNAME()
        qname.len, rest_of_data = Struct('!B %ds' % (len(rest_of_data) - 1)).unpack(rest_of_data)
    if not is_query and (len(question.qnames) < 6):
        question.qnames = question.qnames[::-1]
        question.qnames.append(question.QNAME(7, Struct('!7s').pack("in-addr".encode('utf-8'))))
        question.qnames.append(question.QNAME(4, Struct('!4s').pack("arpa".encode('utf-8'))))
    # print(question.QNAME.len, len(rest_of_data), "\n", rest_of_data)
    question.QTYPE, question.QCLASS, rest_of_data = Struct('!H H %ds' % (len(rest_of_data) - 4)).unpack(rest_of_data)
    question.QTYPE = 255
    question.QCLASS = 1
    # question.printAll()
    return question, rest_of_data, is_query


def handle_server_packet(raw_packet, address, is_query):
    packet_header, rest_of_packet = Struct('!12s %ds' % (len(raw_packet) - 12)).unpack(raw_packet)
    # print("DEBUG--", "packet_header: ", packet_header)
    # header = DNS_PACKET_HEADER((0, 0, 0, 0, 0, 0, 0))
    header, status = parse_packet_header(packet_header, address)  # header type: DNS_PACKET_HEADER+
    log = LOG(str(header.message_id))
    log.print_header(header=header)
    question, rest_of_packet, is_query = parse_packet_question(header, rest_of_packet)
    log.print_question(question=question)
    answers = parse_packet_answer(header, raw_packet, rest_of_packet, is_query)
    if len(answers) == 0:
        packet_to_send = create_refuse_packet(header.message_id)
        return packet_to_send, 0
    else:
        # min_ip = Struct('!I').unpack(answers[0].rdata)[0]
        min_ip = None
        min_ns = None
        min_a_ans = None
        min_ns_ans = None
        A_type_count = 0
        NS_type_count = 0
        for ans in answers:
            # print("answer: ", ans.)
            if ans.ATYPE == 1:
                A_type_count += 1
                tmp_ip = Struct('!I').unpack(ans.rdata)[0]
                if A_type_count == 1:
                    min_ip = tmp_ip
                    min_a_ans = ans
                elif tmp_ip < min_ip:
                    min_ip = tmp_ip
                    min_a_ans = ans
                else:
                    pass
                if check_names(question.qnames, ans.names) and is_query:
                    packet_to_send = create_answer_packet(header=header, answer=ans, is_query=is_query, dns_name=None)
                    log.print_header(header=header)
                    log.print_str("QUESTION\n===============\n===============\nANSWER\n===============\n")
                    log.print_answer_packet(raw_packet=raw_packet, answer=ans)
                    log.print_str("AUTHORITY\n===============\n===============\nADDITIONAL\n===============\n===============")
                    # ans.printAll()
                    return packet_to_send, 0
            elif ans.ATYPE == 2: # NS
                NS_type_count += 1
                tmp_ns, tmp = find_name_in_packet(raw_packet, ans.rdata)
                if NS_type_count == 1:
                    min_ns = tmp_ns
                    min_ns_ans = ans
                elif tmp_ns < min_ns:
                    min_ns = tmp_ns
                    min_ns_ans = ans
                else:
                    pass
            elif ans.ATYPE == 12: # PTR
                dns_name, num = find_name_in_packet(raw_packet, ans.rdata)
                packet_to_send = create_answer_packet(header=header, answer=ans, is_query=is_query, dns_name=dns_name)
                log.print_header(header=header)
                log.print_str("QUESTION\n===============\n===============\nANSWER\n===============\n")
                log.print_answer_packet(raw_packet=raw_packet, answer=ans)
                log.print_str("AUTHORITY\n===============\n===============\nADDITIONAL\n===============\n===============")
                return packet_to_send, 0
            else:
                pass
        if A_type_count > 0:
            # packet_to_send = create_answer_packet(header=header, answer=min_a_ans)
            return None, inet_ntoa(Struct('!I').pack(min_ip))
        elif (is_query == False) and (NS_type_count > 0):
            # packet_to_send = create_answer_packet(header=header, answer=min_ns_ans)
            # print("connect to ", min_ns)
            return None, min_ns
        else:
            packet_to_send = create_refuse_packet(header.message_id)
            log.print_header(header=header)
            log.print_str("QUESTION\n===============\n===============\nANSWER\n===============\n")
            log.print_str("AUTHORITY\n===============\n===============\nADDITIONAL\n===============\n===============")
            return packet_to_send, 0


def handle_client_packet(data, addr):  # addr: (ip, port)
    packet_header, rest_of_packet = Struct('!12s %ds' % (len(data)-12)).unpack(data)
    # print("DEBUG--", "packet_header: ", packet_header)
    # header = DNS_PACKET_HEADER((0, 0, 0, 0, 0, 0, 0))
    header, status = parse_packet_header(packet_header, addr)  # header type: DNS_PACKET_HEADER
    if status == -1:
        return
    else:
        if header.QDCOUNT > 0:
            question, rest_of_packet, is_query = parse_packet_question(header, rest_of_packet)

            packet_to_ask_server = create_ask_root_packet(header, question)
            log = LOG(str(header.message_id))
            log.connect_to_ip(root_server_ip)
            packet_rcv, server_addr = send_packet(packet_to_ask_server, (root_server_ip, 53), 1)
            # write_log(header, question, (root_server_ip, 53))
            packet_to_send, ip = handle_server_packet(packet_rcv, server_addr, is_query)
            while ip != 0:
                # log.connect_to_ip(inet_ntoa(Struct('!I').pack(ip)))
                log.connect_to_ip(ip)
                packet_rcv, server_addr = send_packet(packet_to_ask_server, (ip, 53), 1)
                packet_to_send, ip = handle_server_packet(packet_rcv, server_addr, is_query)
            send_packet(packet_to_send, addr, 0)


serverSock = socket(AF_INET, SOCK_DGRAM)
serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSock.bind((IP, PORT))

while True:
    data, address = serverSock.recvfrom(512)
    # print("DEBUG--", "hello", "world")
    # print("DEBUG--", 'new data from ', address, '\ndata: ', data)
    # print('data is: ', packet_header_struct.unpack(data))
    _thread.start_new_thread(handle_client_packet, (data, address))

