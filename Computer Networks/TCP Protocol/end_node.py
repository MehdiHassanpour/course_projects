from math import ceil, floor

import _thread

from TCP_Packet import *
from random import uniform

# this file includes end node classes: sender and receiver


class SENDER:
    def __init__(self, sender_port=0, receiver_port=0, max_window=32, init_rtt=0,\
                 estimated_rtt=0, sample_rtt=0, window_size=1, sequence_num=0, file_path="file_to_send.txt"):
        self.sender_port = sender_port
        self.receiver_port = receiver_port
        self.max_window = max_window
        self.MSS = 1480 # bytes
        self.window_size = window_size
        self.sequence_num = sequence_num
        self.timers = {}  # {<seq. num>: [<time sent>, <time received>]}
        self.ack_nums_received = []
        self.init_rtt = init_rtt
        self.estimated_rtt = self.init_rtt
        self.sample_rtt = sample_rtt
        self.window_is_linear = False
        self.connection_established = False
        self.in_flight = 0
        self.read_path = "./pipes/sender_" + str(self.sender_port) + "_data.pipe"
        self.write_path = "./pipes/forwardnet_data.pipe"
        self.time_path = "./pipes/sender_" + str(self.sender_port) + "_time.pipe"
        self.file_path = file_path  # "file_to_send.txt"
        file = open(self.file_path, "rb", 0)
        self.file_to_send_from = file.read()
        file.close()
        self.read_file = open(self.read_path, "rb", 0)
        self.time_file = open(self.time_path, "r")
        self.write_file = open(self.write_path, "wb", 0)
        self.time = 0

    def update_rtt(self, sample_rtt):
        estimated_rtt = (1-0.125)*self.estimated_rtt +\
                             (0.125*sample_rtt)
        self.estimated_rtt = ceil(estimated_rtt)

    def update_time(self):
        while self.connection_established:
            # print("DEBUG-- update time: 1st loop")
            ticks = self.time_file.read()
            # print("DEBUG-- ticks: ", ticks)
            if ticks != '':
                # print("DEBUG-- Tick!")
                self.time += ticks.count("tick")
            if (self.timers[self.ack_nums_received[-1]][1] == -1 and self.time -\
                    self.timers[self.ack_nums_received[-1]][0] > (2*self.estimated_rtt)) or \
                    ((self.timers[self.ack_nums_received[-1]][1] - self.timers[self.ack_nums_received[-1]][0]) >\
                                 2*self.estimated_rtt):  # timeout
                # print("DEBUG-- time out for seq num: ", self.ack_nums_received[-1])
                self.max_window = self.window_size // 2 # TODO: REALLY? :)) or max window = pre window size // 2?
                self.window_size = 1
                self.sequence_num = self.ack_nums_received[-1]-1
                data = self.read_data()
                data_packet = self.create_data_packet(data, self.sequence_num + 1)
                data_packet.header.flags |= 0x80
                data_packet.pack()
                send_packet(self.write_file, data_packet.packed_packet)
                self.in_flight = 1
                self.sequence_num += 1
                self.window_is_linear = False
        self.time_file.close()

    def read_data(self):
        # file = open(self.file_path, "rb", 0)
        # data = self.file_to_send_from.read(self.MSS)
        # print("DEBUG-- read_data, seq num: ", self.sequence_num, "first ack: ", self.ack_nums_received[0])
        data = self.file_to_send_from[(self.sequence_num - self.ack_nums_received[0])*self.MSS:\
            (self.sequence_num - self.ack_nums_received[0]+1)*self.MSS]
        return data

    def start_connection(self):  # handshake
        #  send syn packet
        syn_packet = create_syn(sender_port=self.sender_port, receiver_port=self.receiver_port)
        send_packet(write_file=self.write_file, raw_packet=syn_packet.packed_packet)
        self.sequence_num = syn_packet.header.sequence_num
        #  wait for syn-ack and send ack
        self.handle_packet(receive_packet(self.read_file))

    def syn_ack_received(self, new_packet):
        ack_packet = create_ack(sender_port=self.sender_port, receiver_port=self.receiver_port, \
                                sequence_num=self.sequence_num+1, ack_num=0)
        self.sequence_num += 1
        ack_packet.header.ack_num = new_packet.header.sequence_num + 1
        send_packet(self.write_file, ack_packet.packed_packet)

    def ack_received(self, new_packet):
        dupack = False
        cwr_flag = False
        self.ack_nums_received.append(new_packet.header.ack_num)
        if self.ack_nums_received.count(new_packet.header.ack_num) == 4:  # duplicate ACK
            dupack = True
            self.window_size //= 2
            cwr_flag = True
            if self.window_size == 0:
                self.window_size = 1
            self.window_is_linear = True
            self.sequence_num = new_packet.header.ack_num - 1
        if self.window_is_linear:
            if new_packet.header.ack_num >= self.ack_nums_received[-2] + 1 or dupack:
                if not dupack and self.timers[new_packet.header.ack_num-1][1] == -1:
                    self.timers[new_packet.header.ack_num-1] = [self.timers[new_packet.header.ack_num-1][0],\
                                                                self.time]
                    self.update_rtt(self.timers[new_packet.header.ack_num-1][1]-\
                                    self.timers[new_packet.header.ack_num-1][0])
                # print("DEBUG-- Window Status: Linear")
                N = 1
                if self.in_flight == self.window_size:
                    N = 2
                    self.in_flight = 0
                    # self.window_size += 1
                # self.in_flight -= 1
                for i in range(0, N):
                    data = self.read_data()
                    if len(data) != 0:
                        data_packet = self.create_data_packet(data, self.sequence_num + 1)
                        self.sequence_num += 1
                        if cwr_flag:
                            data_packet.header.flags |= 0x80
                            data_packet.pack()
                            cwr_flag = False
                        send_packet(self.write_file, data_packet.packed_packet)
                        self.in_flight += 1
                        self.timers[data_packet.header.sequence_num] = [self.time, -1]
                        # print("DEBUG-- seq:", data_packet.header.sequence_num, "ack:", data_packet.header.ack_num)
                    else:
                        return True
                return False
        else:
            # print("DEBUG-- Window Status: Exponential")
            if new_packet.header.ack_num >= self.ack_nums_received[-2]+1 or dupack:
                if not dupack:
                    try:
                        self.timers[new_packet.header.ack_num-1] = (self.timers[new_packet.header.ack_num-1][0],\
                                                                    self.time)
                        self.update_rtt(self.timers[new_packet.header.ack_num - 1][1]-\
                                    self.timers[new_packet.header.ack_num - 1][0])
                    except:
                        # print("DEBUG--", self.timers)
                # self.sequence_num += 1
                for i in range(0, 2):
                    data = self.read_data()
                    if len(data) != 0:
                        data_packet = self.create_data_packet(data, self.sequence_num+1)
                        if cwr_flag:
                            data_packet.header.flags |= 0x80
                            data_packet.pack()
                            cwr_flag = False
                        self.sequence_num += 1
                        send_packet(self.write_file, data_packet.packed_packet)
                        self.in_flight += 1
                        self.timers[data_packet.header.sequence_num] = [self.time, -1]
                        # print("DEBUG-- seq:", data_packet.header.sequence_num, "ack:", data_packet.header.ack_num)
                    else:
                        return True
                self.window_size = (self.window_size + 1) // 2
                if self.window_size == 0:
                    self.window_size = 1
            # self.in_flight
            else:
                # print("DEBUG-- ACK IS NOT VALID! ack < seq")
                return False

    def create_data_packet(self, payload, sequence_num):
        data_packet = TCP_PACKET()
        data_packet.create_packet(src_port=self.sender_port, dst_port=self.receiver_port,\
                                  sequence_num=sequence_num, offset_reserved_ns=0x50,\
                                  flags=0, window_size=self.window_size, payload=payload)
        # self.sequence_num += 1
        return data_packet

    def create_fin(self, sequence_num):
        fin_packet = TCP_PACKET()
        fin_packet.create_packet(src_port=self.sender_port, dst_port=self.receiver_port,\
                                  sequence_num=sequence_num, offset_reserved_ns=0x50,\
                                  flags=0x01, window_size=self.window_size)
        return fin_packet

    def handle_packet(self, new_packet):
        if new_packet.header.flags == 0x12:  # syn-ack received
            # print("DEBUG--SYN-ACK Received, Sending ACK")
            self.syn_ack_received(new_packet)
            self.connection_established = True

        elif new_packet.header.flags == 0x10:
            # print("DEBUG--ACK Received")
            return self.ack_received(new_packet)
        else:
            pass

    def main(self):
        self.start_connection()
        # print("DEBUG-- Handshake completed, connection established")
        _thread.start_new_thread(self.update_time, ())
        sendFinished = False
        waiting_for_ack = False
        # self.expected_ack_num = []
        self.ack_nums_received.append(self.sequence_num)
        data = self.read_data()
        data_packet = self.create_data_packet(data, self.sequence_num+1)  # first packet
        send_packet(self.write_file, data_packet.packed_packet)
        # print("DEBUG-- seq:", data_packet.header.sequence_num, "ack:", data_packet.header.ack_num)
        self.in_flight += 1
        self.sequence_num += 1
        self.timers[data_packet.header.sequence_num] = [self.time, -1]
        # print("DEBUG-- send data packet, seq.no.: ", data_packet.header.sequence_num)
        while sendFinished == False or waiting_for_ack == True:
            print(sendFinished, waiting_for_ack)
            waiting_for_ack = False
            for key, value in self.timers.items():
                if value[1] == -1:
                    # print("waiting for ", key, value)
                    waiting_for_ack = True
                    break
                else:
                    waiting_for_ack = False
            if sendFinished == True and waiting_for_ack == False:
                break
            if self.in_flight == self.max_window and self.window_size == self.max_window:
                # print("DEBUG-- window size reached threshold, window size:", self.window_size)
                self.window_is_linear = True
                self.window_size //= 2
            ack_packet = receive_packet(self.read_file)
            # self.in_flight -= 1
            # print("DEBUG-- receive packet: seq.no:", self.sequence_num, "last_acked: ", self.ack_nums_received[-1], "ack no: ", ack_packet.header.ack_num)
            sendFinished = self.handle_packet(ack_packet)

        fin_packet = self.create_fin(self.sequence_num+1)
        send_packet(self.write_file, fin_packet.packed_packet)
        # print("DEBUG-- FIN SENT")
        ack_packet = receive_packet(self.read_file)
        if ack_packet.header.flags == 0x10: #ack for fin received
            fin_from_receiver = receive_packet(self.read_file)
            if fin_from_receiver.header.flags == 0x01:  # fin from receiver
                ack_packet = create_ack(self.sender_port, self.receiver_port, 0,0)
                send_packet(self.write_file, ack_packet.packed_packet)
                self.connection_established = False
                return

    def log(self):
        print("######SENDER######\nsender port:", self.sender_port,\
              "\nreceiver port:", self.receiver_port,\
              "\nmax_window:", self.max_window,\
              "\nsequence num:", self.sequence_num,\
              "\ninitial RTT:", self.init_rtt, "\nestimated RTT:", self.estimated_rtt,\
              "\nsample RTT:", self.sample_rtt)


class RECEIVER:
    def __init__(self, receiver_port=0):
        self.receiver_port = receiver_port
        self.sender_port = 0
        self.sequence_num = 0
        self.sender_data_offset = 0
        self.ack_num_to_send = 0
        self.read_path = "./pipes/receiver_"+str(self.receiver_port)+"_data.pipe"
        self.write_path = "./pipes/backwardnet_data.pipe"
        self.read_file = open(self.read_path, "rb", 0)
        self.write_file = open(self.write_path, "wb", 0)
        self.MSS = 1480
        self.data = bytearray(self.MSS*1000)
        self.seq_nums_received = []

    def log(self):
        print("######RECEIVER#######\nreceiver port:", self.receiver_port, "\nsender port",\
              self.sender_port, "\ndata:", str(self.data, "Latin-1"), "\nseq. num:",\
              self.sequence_num, "\nack_num_to_send:", self.ack_num_to_send)

    def handle_syn_received(self, new_packet):
        self.sender_port = new_packet.header.src_port
        syn_ack_packet = create_syn_ack(self.receiver_port, new_packet.header.src_port,\
                                        int(floor(uniform(0, (2 ** 32) - 1))),\
                                        new_packet.header.sequence_num+1)
        send_packet(write_file=self.write_file, raw_packet=syn_ack_packet.packed_packet)
        # print("DEBUG-- packet to send: ")
        # syn_ack_packet.log()
        self.sequence_num = syn_ack_packet.header.sequence_num
        self.ack_num_to_send = new_packet.header.sequence_num + 2

    def handle_ack_received(self, new_packet):
        self.sender_data_offset = new_packet.header.sequence_num + 1
        pass

    def store_data(self, index, data):
        for i in range((index - self.sender_data_offset)*self.MSS, len(data)):
            self.data[i] = data[i-(index - self.sender_data_offset)*self.MSS]

        # self.data_offset += len(data)
        # if len(self.data) == 0:
        #     self.data = bytearray(self.MSS)
        # else:

    def handle_packet(self, new_packet):
        if new_packet.header.flags == 0x02:  # syn received
            # print("DEBUG-- SYN Received")
            self.handle_syn_received(new_packet)
            return 0
        elif new_packet.header.flags == 0x10:  # ack received
            # print("DEBUG-- ACK Received, Connection Established")
            self.handle_ack_received(new_packet)
            return 0
        elif new_packet.header.flags == 0x01:  # FIN received
            ack_packet = create_ack(self.receiver_port, new_packet.header.src_port,0, new_packet.header.sequence_num+1)
            send_packet(self.write_file, ack_packet.packed_packet)
            fin_packet = TCP_PACKET()
            fin_packet.create_packet(self.receiver_port, new_packet.header.src_port, 0, 0, 0, 0x01, 0)
            send_packet(self.write_file, fin_packet.packed_packet)
            ack_packet = receive_packet(self.read_file)
            return -1

        else:
            # TODO: check packet is valid or not(checksum)
            # print("DEBUG-- Data received: ", str(new_packet.payload, "Latin-1"))
            # self.store_data(index=new_packet.header.sequence_num, data=new_packet.payload)
            if not new_packet.header.sequence_num in self.seq_nums_received:
                self.store_data(index=new_packet.header.sequence_num, data=new_packet.payload)
                self.seq_nums_received.append(new_packet.header.sequence_num)
                if self.ack_num_to_send == new_packet.header.sequence_num:
                    self.ack_num_to_send += 1
                    while self.ack_num_to_send in self.seq_nums_received:
                        self.ack_num_to_send += 1

            # else: # duplicate packet
                # pass
            ack_packet = create_ack(new_packet.header.src_port, new_packet.header.dst_port, 0, self.ack_num_to_send)
            send_packet(self.write_file, ack_packet.packed_packet)
            # print("DEBUG-- seq:", ack_packet.header.sequence_num, "ack:", ack_packet.header.ack_num)
            return 0

    def main(self):
        while True:
            new_packet = receive_packet(self.read_file)
            # print("DEBUG--new packet received:")
            # new_packet.log()
            if self.handle_packet(new_packet) == -1:
                break