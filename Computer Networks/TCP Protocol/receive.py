from end_node import *
import sys

receiver = RECEIVER(int(sys.argv[1]))
receiver.main()
receiver.read_file.close()
receiver.write_file.close()