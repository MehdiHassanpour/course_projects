rm algorithms/edf.out
rm algorithms/ldf.out
rm algorithms/dss.out
g++ -o algorithms/edf.out algorithms/edf.cpp
g++ -o algorithms/ldf.out algorithms/ldf.cpp
g++ -o algorithms/dss.out algorithms/dss.cpp
python3 _run.py $1 $2
