from end_node import *
import sys

sender = SENDER(sender_port=int(sys.argv[1]), receiver_port=int(sys.argv[2]), max_window=int(sys.argv[4])\
                , init_rtt=int(sys.argv[3]), file_path=str(sys.argv[5]))
sender.main()
sender.read_file.close()
sender.write_file.close()
