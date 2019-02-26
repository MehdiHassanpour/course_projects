import sys
import os

alg = str(sys.argv[1])
input_file = str(sys.argv[2])
print(alg, input_file)
os.system("./algorithms/"+ alg+ ".out < " + input_file)
