/*
* in this code we implement Latest Deadline First algorithm
* to schedule Aperiodic jobs
*/
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

int LatestDeadlineFirst(vector<Job> jobs, vector<vector<int> > precedence);
vector<int> sort_on_deadline(vector<Job> jobs);

int main() {
	vector<Job> jobs;
	cout << "LDF Algorithm" << endl;

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
	cout << "Enter the number of precedence relations" << endl;
	int precedence_num = 0;
	cin >> precedence_num;
	cout << "Enter the edges of precedence graph:" << endl;
	for(int i = 0; i < precedence_num; i++) {
		int pre, post;
		cin >> pre >> post;
		precedence[pre].push_back(post);
		reverse_precedence[post].push_back(pre);
	}
	LatestDeadlineFirst(jobs, precedence);
	system("./gantt_chart_creator LatestDeadlineFirst");
	return 0;
}

vector<int> sort_on_deadline(vector<Job> jobs) { /*job index with latest deadline at 0 */
	vector<int> result;
	bool *visited = new bool[(int)jobs.size()];
	for(int i = 0; i < (int)jobs.size(); i++) {
		visited[i] = false;
	}

	for(int i = 0; i < (int)jobs.size(); i++) {
		int d = -1;
		int index = 0;
		for(int j = 0; j < (int)jobs.size(); j++) {
			if (visited[j])
				continue;
			if (jobs[j].deadline > d) {
				index = j;
				d = jobs[j].deadline;
			}
		}
		result.push_back(index);
		visited[index] = true;
	}

	return result;
}

int LatestDeadlineFirst(vector<Job> jobs, vector<vector<int> > precedence) {
	vector<pair<int, Job> > scheduled;
	int latest_deadline = 0; 
	int jobs_count = (int)jobs.size();

	bool *is_scheduled = new bool[jobs_count];
	for(int i = 0; i < jobs_count; i++) {
		is_scheduled[i] = false;
	}

	/* sorting jobs based on deadline */
	vector<int> sorted_index = sort_on_deadline(jobs);
	latest_deadline = jobs[sorted_index[0]].deadline;

	while ((int)scheduled.size() < jobs_count) {
		for (int i = 0; i < (int)sorted_index.size(); i++) {
			if (is_scheduled[sorted_index[i]]) {
				continue;
			}
			bool can_be_scheduled = true;
			for(int j = 0; j < (int)precedence[sorted_index[i]].size(); j++) {
				// cout << "precedence\t" << precedence[sorted_index[i]][j] << "\t" << sorted_index[i] << endl;
				if (!is_scheduled[precedence[sorted_index[i]][j]]) {
					can_be_scheduled = false;
					// cout << "precedence\t" << precedence[sorted_index[i]][j] << "\t" << sorted_index[i] << endl;
					break;
				}
			}
			// cout << "processing " << sorted_index[i] << "\t" << can_be_scheduled << endl;
			if (can_be_scheduled) {
				scheduled.push_back(pair<int, Job> (sorted_index[i], jobs[sorted_index[i]]));
				is_scheduled[sorted_index[i]] = true;
				break;
			}

		}

	}
	/* pop from stack and process the jobs */
	int current_time = 0;
	for(int i = (int)scheduled.size()-1; i >= 0; i--) {
		scheduled[i].second.startTime = current_time;
		current_time += scheduled[i].second.computationTime;
		scheduled[i].second.finishTime = current_time;
	}
	ofstream output;
	output.open("scheduled_jobs.txt");
	output << jobs_count << endl;
	for (int i = 0; i < jobs_count; i++) {
		cout << "Job " << scheduled[i].first << "\t" << scheduled[i].second.startTime << "\t" << scheduled[i].second.finishTime << endl;
		output << scheduled[i].first+1 << " " << scheduled[i].second.arrivalTime << " "\
		 << scheduled[i].second.deadline << " " << scheduled[i].second.computationTime << " " << scheduled[i].second.finishTime << " ";
		output << scheduled[i].second.startTime << " " << scheduled[i].second.computationTime << endl;		 
	}
	output.close();
}