from socket import *
from lib import *
from pprint import pprint
from threading import *
from struct import *
import ctypes
import sys

IP = '127.0.0.1'
PORT = 15353
BUFFER_SIZE = 1024
MSG = 258


class myThread (Thread):
    def __init__(self, clientSocket):
        super().__init__()
        self.clientSocket = clientSocket

    def run(self):
        data = self.clientSocket.recvfrom(BUFFER_SIZE)
        self.clientSocket.close()
        print('raw data: ', data)
        print(packet_header_struct.unpack(data[0]))


clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# MESSAGE = Struct('!12s 5s 10s').pack("123456789012".encode('utf-8'), "12313516".encode('utf-8'), "aziz e del".encode('utf-8'))
MESSAGE = Struct('!HBBHHHH B6sB3sBHH HHHH').pack(2,0,1,1,0,0,0, 6,"google".encode('utf-8'),3,"com".encode('utf-8'),0,0,0, 1,2,3,4)
iquery_msg = Struct('!HBBHHHH B2sB2sB2sB2sBHH').pack(3,0,1,1,0,0,0, 2,"10".encode('utf-8'),2,"10".encode('utf-8'),2,"10".encode('utf-8'),2,"10".encode('utf-8'),0,0,0)
print("message packed: ", MESSAGE)
clientSocket.sendto(iquery_msg, (IP, PORT))