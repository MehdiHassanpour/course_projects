import _thread

from .end_node import *

tmp = input("run as a sender or receiver?")
if tmp == "sender":
    sender = SENDER(sender_port=1234, receiver_port=5678, max_window=30, init_rtt=10)
    sender.main()
    sender.read_file.close()
    sender.write_file.close()
    # sender.file_to_send_from.close()
elif tmp == "receiver":
    receiver = RECEIVER(5678)
    receiver.main()
    receiver.read_file.close()
    receiver.write_file.close()
