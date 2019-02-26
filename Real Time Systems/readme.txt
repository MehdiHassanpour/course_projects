In this project, we implemented 3 algorithms to schedule jobs.
- Latest Deadline First (with precedence)
- (Modified) Earliest Deadline First (with precedence)
- Dynamic Sporadic Server


**** How to Run ****
- run ./install.sh for project requirements
- run ./run.sh <algorithm> <input> 
where <algorithm> can be one of the
- ldf
- edf
- dss
and <input> is the input file containing jobs and their precedence graph if required.

example:
./run.sh ldf input_examples/ldf_input.txt

**** input file format ****
**input for ldf and edf:
<number of jobs>
in next lines for each job: 
<arrival time> <computation time> <deadline>
<number of precedence graph's edges>
for each edge:
<source> <destination>

**input for dss:
<Server Period>
<Server Capacity>
<number of jobs>
in each line:
<arrival time> <computation time> <period>
for aperiodic jobs, insert -1 as period.