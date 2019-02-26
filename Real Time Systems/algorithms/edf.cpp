#include <iostream>
#include <vector>
#include <algorithm>
#include <map>
#include <climits>
#include <fstream>
using namespace std;

struct Job
{
	int arrivalTime;
	int computationTime;
	int deadline;	
	int startTime;
	int finishTime;		
};

void _EarliestDeadlineFirst(vector<Job> jobs);
vector<Job> modifyReleaseTime(vector<Job> jobs, vector<vector<int> > precedence, vector<vector<int> > reverse_precedence);
vector<Job> modifyDeadline(vector<Job> jobs, vector<vector<int> > precedence, vector<vector<int> > reverse_precedence);
void EarliestDeadlineFirst(vector<Job> jobs, vector<vector<int> > precedence, vector<vector<int> > reverse_precedence);

int main() {
	vector<Job> jobs;
	cout << "EDF Algorithm" << endl;
	cout << "Enter the number of jobs: ";

	int jobNumbers;
	cin >> jobNumbers;

	for (int i = 0; i < jobNumbers; ++i)
	{
		cout << "Job " << i+1 << endl;

		Job job;

		cout << "arrival time: ";
		cin >> job.arrivalTime;
		cout << "computation time: ";
		cin >> job.computationTime;
		cout << "deadline: ";
		cin >> job.deadline;

		jobs.push_back(job);

	}
	vector<vector<int> > precedence, reverse_precedence;
	for(int i = 0; i < jobNumbers; i++) {
		vector<int> tmp;
		precedence.push_back(tmp);
		reverse_precedence.push_back(tmp);
	}
	cout << "Enter the number of precedence relations: ";
	int precedence_num = 0;
	cin >> precedence_num;
	cout << "Enter edges of the precedence graph:" << endl;
	for(int i = 0; i < precedence_num; i++) {
		int pre, post;
		cin >> pre >> post;
		precedence[pre].push_back(post);
		reverse_precedence[post].push_back(pre);
	}
	EarliestDeadlineFirst(jobs, precedence, reverse_precedence);
	system("./gantt_chart_creator EarliestDeadlineFirst");
	return 0;
}
void _EarliestDeadlineFirst(vector<Job> jobs) {
	vector<Job> jobs_copy = jobs;
	map<int, vector<pair<int, int> > > scheduled;
	int current_time = 0;
	int finished_count = 0;
	
	int next_job_index = -1;
	int last_job_index = -1;
	
	while (true) {
		int next_job_index = -1; 
		int earliest_deadline = INT_MAX;
		for (vector<Job>::iterator it = jobs_copy.begin(); it != jobs_copy.end(); it++) {
			if ((it->computationTime != 0) && (it->arrivalTime <= current_time)) {
				if (it->deadline < earliest_deadline) {
					next_job_index = it - jobs_copy.begin();
					earliest_deadline = it->deadline;
				}
			}
		}
		if (finished_count == (int)jobs.size()) {
			scheduled[last_job_index][scheduled[last_job_index].size()-1].second = current_time - scheduled[last_job_index][scheduled[last_job_index].size()-1].first;
			break;
		}
		if (next_job_index == -1)
			continue;

		if (last_job_index != -1)
			scheduled[last_job_index][scheduled[last_job_index].size()-1].second = current_time - scheduled[last_job_index][scheduled[last_job_index].size()-1].first;
		
		jobs_copy[next_job_index].computationTime--;
		
		if (jobs_copy[next_job_index].computationTime == 0) {
			finished_count++;
			jobs_copy[next_job_index].finishTime = current_time+1;
		}
		
		if (last_job_index == next_job_index) {
			current_time++;
			continue;
		}
		
		if (scheduled.find(next_job_index) != scheduled.end()) {
			scheduled[next_job_index].push_back(pair<int, int> (current_time, -1)); //scheduled[next_job_index].push_back(current_time);
		}
		
		else {
			vector<pair<int, int> > tmp;
			tmp.push_back(pair<int, int> (current_time, -1)); //tmp.push_back(current_time)
			scheduled[next_job_index] = tmp;
		}
		current_time++;
		last_job_index = next_job_index;
	}
	ofstream output;
	output.open("scheduled_jobs.txt");
	output << (int)jobs.size() << endl;
	for (map<int, vector<pair<int, int> > >::iterator it1 = scheduled.begin(); it1 != scheduled.end(); it1++) {
		cerr << "Job " << it1->first << ":" << endl;
		output << it1->first + 1 << " " << jobs[it1->first].arrivalTime\
		<< " " << jobs[it1->first].deadline << " " << jobs[it1->first].computationTime\
		<< " " << jobs_copy[it1->first].finishTime << " ";
		for (vector<pair<int, int> >::iterator it2 = it1->second.begin(); it2 != it1->second.end(); it2++) {
			cout << it2->first << "\t" << it2->second << endl;
			output << it2->first << " " << it2->second << " ";
		}
		output << endl;
	}
	output.close();
}
vector<Job> modifyReleaseTime(vector<Job> jobs, vector<vector<int> > precedence, vector<vector<int> > reverse_precedence) {
	bool* job_modified = new bool[(int)jobs.size()];
	for(int i = 0; i < (int)jobs.size(); i++) {
		job_modified[i] = true;
	}
	for (int i = 0; i < (int)precedence.size(); i++) {
		for(int j = 0; j < (int)precedence[i].size(); j++) {
			job_modified[precedence[i][j]] = false;
		}
	}
	while(true){
		bool modified = false;
		for (int i = 0; i < (int)reverse_precedence.size(); i++) {
			if (job_modified[i]) {
				continue;
			}
			bool can_be_modified = true;
			for(int j = 0; j < (int)reverse_precedence[i].size(); j++) {
				if (!job_modified[reverse_precedence[i][j]]) {
					can_be_modified = false;
					break;
				}
			}
			if (can_be_modified) {
				for (int j = 0; j < (int)reverse_precedence[i].size(); j++) {
					jobs[i].arrivalTime = max(jobs[i].arrivalTime, jobs[reverse_precedence[i][j]].arrivalTime + jobs[reverse_precedence[i][j]].computationTime);
				}
				job_modified[i] = true;
				modified = true;
				break;
			}
		}
		if (!modified)
			break;
	}
	return jobs;
}
vector<Job> modifyDeadline(vector<Job> jobs, vector<vector<int> > precedence, vector<vector<int> > reverse_precedence) {
	bool* deadline_modified = new bool[(int)jobs.size()];
	for(int i = 0; i < (int)jobs.size(); i++) {
		deadline_modified[i] = true;
	}
	for (int i = 0; i < (int)reverse_precedence.size(); i++) {
		for(int j = 0; j < (int)reverse_precedence[i].size(); j++) {
			deadline_modified[reverse_precedence[i][j]] = false;
		}
	}
	while(true){
		bool modified = false;
		for (int i = 0; i < (int)precedence.size(); i++) {
			if (deadline_modified[i]) {
				continue;
			}
			bool can_be_modified = true;
			for(int j = 0; j < (int)precedence[i].size(); j++) {
				if (!deadline_modified[precedence[i][j]]) {
					can_be_modified = false;
					break;
				}
			}
			if (can_be_modified) {
				for (int j = 0; j < (int)precedence[i].size(); j++) {
					jobs[i].deadline = min(jobs[i].deadline, jobs[precedence[i][j]].deadline - jobs[precedence[i][j]].computationTime);
				}
				deadline_modified[i] = true;
				modified = true;
				break;
			}
		}
		if (!modified)
			break;
	}
	return jobs;
}

void EarliestDeadlineFirst(vector<Job> jobs, vector<vector<int> > precedence, vector<vector<int> > reverse_precedence) {
	jobs = modifyReleaseTime(jobs, precedence, reverse_precedence);
	
	jobs = modifyDeadline(jobs, precedence, reverse_precedence);
	
	_EarliestDeadlineFirst(jobs);
	
	return;
}
