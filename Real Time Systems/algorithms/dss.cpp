#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <fstream>

#define INFTY (99999999L)
#define EPSILON (0.001)
#define FINISH_SIM 24
#define OUT_FILE "scheduled_jobs.txt"

using namespace std;

struct Job {
    int id;
    double deadline;
    double computation;
    bool periodic;
};

struct State {
    int job; //job index for doing job and -1 for idle
    double since;
};

bool equal(double lhs, double rhs) {
    return abs(lhs - rhs) < EPSILON;
}

struct DoubleComparator {
    
    bool operator() (const double &lhs, const double &rhs) const {
        return lhs + EPSILON < rhs;
    }
    
};

struct QComparator {
    
    bool operator() (const pair<double, Job> &lhs, const pair<double, Job> &rhs) const {
        
        if (!::equal(lhs.first, rhs.first)) {
            return lhs.first < rhs.first;
        } else if (!::equal(lhs.second.deadline, rhs.second.deadline)) {
            return lhs.second.deadline < rhs.second.deadline;
        } else if (lhs.second.periodic != rhs.second.periodic) {
            return !lhs.second.periodic;
        } else {
            return lhs.second.computation < rhs.second.computation;
        }
        
    }
    
};

class DSS {

private:
    double finish;
    double ts;
    double cs;
    State state;
    set<double, DoubleComparator> keyframes;
    
    int currentFrame;
    set<double, DoubleComparator>::iterator currentKeyIt;
    double now;
    
    set<pair<double, Job>, QComparator> jobQ;
    map<int, Job> jobs;
    int numOfAPs;
    int jobCounter;
    
    struct {
        bool predicting;
        double consumed;
        double time;
    } replenishment;
    
    map<double, double, DoubleComparator> reps;
    
    State handleKeyframe();
    int edf();
    void progressWork(int idx, double amount);
    void consumeCS(double amount);
    
public:
    DSS(double ts, double cs, double finish);
    void addJob(double release, double computation, double period); //-1 period for aperiodic
    vector<pair<State, double> > schedule();
    int getJobCounter() const;
    
};

void print4Gannt(vector<State> sched, int numOfJobs);
vector<pair<double, double> > getStartsOfJob(vector<State> sched, int idx);
vector<State> smooth(vector<pair<State, double> > sched);

int DSS::getJobCounter() const {
    return jobCounter;
}

DSS::DSS(double ts, double cs, double finish) {
    this->ts = ts;
    this->cs = cs;
    this->finish = finish;
    state.job = -1; //idle
    state.since = 0;
    numOfAPs = 0;
    replenishment.predicting = false;
    replenishment.consumed = 0;
    jobCounter = 0;
    keyframes.insert(0);
    currentFrame = 0;
    currentKeyIt = keyframes.begin();
    now = 0;
}

State DSS::handleKeyframe() {
    now = *(currentKeyIt);
    Job currentJob;
    
    while (!jobQ.empty()) {
        
        if (jobQ.begin()->first > now) {
            break;
        }
        
        jobs.insert(make_pair(jobQ.begin()->second.id, jobQ.begin()->second));
        
        if (!jobQ.begin()->second.periodic) {
            numOfAPs++;
        }
        
        cerr << "[" << now << "]\t" << "j" << jobQ.begin()->second.id + 1 << " arrived.\n";
        
        jobQ.erase(jobQ.begin());
    }
    
    while (!reps.empty()) {
        
        if (reps.begin()->first > now) {
            break;
        }
        
        cs += reps.begin()->second;
        cerr << "[" << now << "]\t" << "Cs increased by " << reps.begin()->second << ".\n";
        reps.erase(reps.begin());
    }
    
    if (state.job != -1) {
        currentJob = jobs.at(state.job);
        
        if (!currentJob.periodic) {
            consumeCS(now - state.since);
            cerr << "[" << now << "]\t" << "Cs decreased by " << now - state.since << " toatling to " << cs << ".\n";
        }
        
        progressWork(state.job, now - state.since);
    }
    
    int newJob = edf();
    
    if (newJob != -1) {
        
        if (!jobs.at(newJob).periodic) {
            bool shouldPredict = false;
            
            if (state.job == -1) {
                shouldPredict = true;
            } else if (currentJob.periodic) {    
                shouldPredict = true;
            }
        
            if (shouldPredict) {
                assert(replenishment.predicting == false);
                replenishment.predicting = true;
                replenishment.time = now + ts;
                replenishment.consumed = 0;
                cerr << "[" << now << "]\t" << "RT set for " << replenishment.time << ".\n";
                keyframes.insert(replenishment.time);
            }
            
        }
        
    }
    
    if ( replenishment.predicting && (equal(cs, 0) || numOfAPs == 0) ) {
        reps[replenishment.time] += replenishment.consumed;
        cerr << "[" << now << "]\t" << "RA set to " << replenishment.consumed << " totaling to " << reps[replenishment.time] << ".\n";
        replenishment.predicting = false;
    }
    
    double checkpoint;
    
    if (newJob != -1) {
        
        if (jobs.at(newJob).periodic) {
            checkpoint = now + jobs.at(newJob).computation;
        } else {
            checkpoint = now + ( (cs < jobs.at(newJob).computation) ? (cs) : (jobs.at(newJob).computation) );
        }
        
        cerr << "[" << now << "]\t" << "Checkpoint set for " << checkpoint << ".\n";
    }
    
    keyframes.insert(checkpoint);
    state.job = newJob;
    state.since = now;
    currentFrame++;
    currentKeyIt++;
    return state;
}

void DSS::progressWork(int idx, double amount) {
    assert(jobs.at(idx).computation >= amount - EPSILON);
    jobs.at(idx).computation -= amount;
    cerr << "[" << now << "]\t" << "j" << idx + 1 << " remaining computation set to " << jobs.at(idx).computation << ".\n";
    
    if (equal(jobs.at(idx).computation, 0)) {
        
        if (!jobs.at(idx).periodic) {
            numOfAPs--;
        }
        
        jobs.erase(idx);
        cerr << "[" << now << "]\t" << "j" << idx + 1 << " done.\n";
    }
    
}

void DSS::consumeCS(double amount) {
    assert(cs >= amount - EPSILON);
    cs -= amount;
    assert(replenishment.predicting == true);
    replenishment.consumed += amount;
    cerr << "[" << now << "]\t" << "Replenishment amount increased by " << amount << " toatling to " << replenishment.consumed << ".\n";
}

int DSS::edf() {
    double minDeadline = INFTY;
    int jIdx = -1;
    bool onlyP = false;
    double serverDeadline = *(currentKeyIt) + ts;
    
    if (equal(cs, 0)) {
        onlyP = true;
    }
    
    for (map<int, Job>::iterator it = jobs.begin(); it != jobs.end(); it++) {
        
        if ( (!it->second.periodic) && (onlyP) ) {
            continue;
        }
        
        double currentDeadline = (it->second.periodic) ? (it->second.deadline) : (serverDeadline);

        if (currentDeadline < minDeadline) {
            minDeadline = currentDeadline;
            jIdx = it->first;
        } else if (equal(currentDeadline, minDeadline)) {
            
            if (jIdx != -1) {
                
                if ( (jobs.at(jIdx).periodic) && (!it->second.periodic) ) {
                    jIdx = it->first;
                } else if (jobs.at(jIdx).computation > it->second.computation + EPSILON) {
                    jIdx = it->first;
                }
                
            }
            
        }
        
    }
    
    cerr << "[" << now << "]\t" << "j" << jIdx + 1 << " chosen by EDF with deadline " << minDeadline << ".\n";
    return jIdx;
}

void DSS::addJob(double release, double computation, double period) {
    int id = jobCounter++;
    
    if (period > 0) {
        
        for (double t = release; t < finish; t += period) {
            Job j;
            j.id = id;
            j.computation = computation;
            j.deadline = t + period;
            j.periodic = true;
            jobQ.insert(make_pair(t, j));
            keyframes.insert(t);
        }
        
    } else {
        Job j;
        j.id = id;
        j.computation = computation;
        j.deadline = -1;
        j.periodic = false;
        jobQ.insert(make_pair(release, j));
        keyframes.insert(release);
    }
    
}

vector<pair<State, double> > DSS::schedule() {
    vector<pair<State,double> > ret;
    
    while (currentFrame != keyframes.size()) {
        ret.push_back(make_pair(handleKeyframe(), cs));
    }
    
    return ret;
}

struct Storage {
    double arrival;
    double computation;
};

vector<Storage> storage;

void print4Gannt(vector<State> sched, int numOfJobs, ostream &out) {
    out << numOfJobs << endl;
    
    for (int i = 0; i < numOfJobs; i++) {
        vector<pair<double, double> > starts = getStartsOfJob(sched, i);
        out << i + 1 << " "; //counter
        out << storage.at(i).arrival << " "; //arrival
        out << FINISH_SIM << " "; //deadline
        out << storage.at(i).computation << " "; //computation
        out << starts.at(starts.size() - 1).first + starts.at(starts.size() - 1).second << " "; //finish
        
        for (int j = 0; j < starts.size(); j++) {
            out << starts.at(j).first << " " << starts.at(j).second << " ";
        }
        
        out << endl;
    }
    
}

vector<State> smooth(vector<pair<State, double> > sched) {
    vector<State> ret;
    
    int lastJob = -10;
    
    for (int i = 0; i < sched.size(); i++) {
        
        if (sched.at(i).first.job != lastJob) {
            ret.push_back(sched.at(i).first);
            lastJob = sched.at(i).first.job;
        }
        
    }
    
    return ret;
}

vector<pair<double, double> > getStartsOfJob(vector<State> sched, int idx) {
    vector<pair<double, double> > ret;
    double until;
    
    for (int i = 0; i < sched.size(); i++) {
        
        if (sched.at(i).job == idx) {
            
            if (i == sched.size() - 1) {
                until = FINISH_SIM;
            } else {
                until = sched.at(i + 1).since;
            }
            
            ret.push_back(make_pair(sched.at(i).since, until - sched.at(i).since));
        }
        
    }
    
    return ret;
}

int main(int argc, const char *argv[]) {
    double ts, cs;
    ofstream outFile(OUT_FILE);
    int howManyJobs;
    cout << "----Dynamic Sporadic Server----\n";
    cout << "Ts?\t";
    cin >> ts;
    cout << "Cs?\t";
    cin >> cs;
    DSS dss(ts, cs, FINISH_SIM);
    cout << "How many jobs?\t";
    cin >> howManyJobs;
    cout << "Specify each job in a separate line as follows: (period:-1 for aperiodic jobs)\n";
    cout << "Arrival_Time Computation_Time Period\n";
    
    for (int i = 0; i < howManyJobs; i++) {
        double arrival, period, computation;
        cin >> arrival >> computation >> period;
        dss.addJob(arrival, computation, period);
        Storage newS;
        newS.arrival = arrival;
        newS.computation = computation;
        storage.push_back(newS);
    }
    
    vector<pair<State, double> > schedule = dss.schedule();
    
    // cout << "TIME\tJOB\tCs\n";
    //
    // for (int i = 0; i < schedule.size(); i++) {
    //     cout << schedule.at(i).first.since << "\t" << schedule.at(i).first.job + 1 << "\t" << schedule.at(i).second << endl;
    // }
    
    print4Gannt(smooth(schedule), dss.getJobCounter(), outFile);
    outFile.close();
    
    system("./gantt_chart_creator 'Dynamic Sporadic Server'");
    return 0;
}