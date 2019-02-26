/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   main.cpp
 * Author: shahrooz
 *
 * Created on February 7, 2019, 8:20 PM
 */

#include <cstdlib>
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include "Job.h"
#include "Defines.h"

using namespace std;

/*
 * 
 */

inline bool file_exist (const std::string& name) {
    if (FILE *file = fopen(name.c_str(), "r")) {
        fclose(file);
        return true;
    } else {
        return false;
    }   
}

int read_file(string file_name, vector <Job*> &jobs, int &min_time, int &max_time){
    
    ifstream in(file_name, ios::in);
    if(!in.is_open()){
        cout << "Can't open the file " << file_name << endl;
        return FILE_OPEN_ERR;
    }
    
    int number_of_jobs;
    
    in >> number_of_jobs;
    string line;
    int ttemp;
    int number_temp;
    string name;
    getline(in, line);
    for(int i = 0; i < number_of_jobs; i++){
        name = "J ";
//        name += to_string(i + 1);
        getline(in, line);
        stringstream temp(line);
        jobs.push_back(new Job(name));
        temp >> number_temp;
        jobs[i]->set_number(number_temp);
        temp >> jobs[i]->arrival_time;
        min_time = min(min_time, jobs[i]->arrival_time);
        max_time = max(max_time, jobs[i]->arrival_time);
        temp >> jobs[i]->deadline;
        min_time = min(min_time, jobs[i]->deadline);
        max_time = max(max_time, jobs[i]->deadline);
        temp >> jobs[i]->computation_time;
        min_time = min(min_time, jobs[i]->computation_time);
        max_time = max(max_time, jobs[i]->computation_time);
        temp >> jobs[i]->finish_time;
        min_time = min(min_time, jobs[i]->finish_time);
        max_time = max(max_time, jobs[i]->finish_time);
        
        
        
        while(temp >> ttemp){
            jobs[i]->start_time.push_back(ttemp);
            min_time = min(min_time, ttemp);
            max_time = max(max_time, ttemp);
            temp >> ttemp;
            jobs[i]->comp_per_start.push_back(ttemp);
        }
    }
    
    in.close();
    
    return OK;
}

int do_it_for_a_file(string schedule_name, string file_name, int method = 0){

//    Job::color_number = 13; // color initializing
    
    string json_output;
    
    json_output = "{\n";
    
    json_output += "  \"packages\": [\n";
    
    json_output += "    {\n\
      \"label\": \"\",\n\
      \"start\": 0,\n\
      \"end\": 0\n\
    },\n";
    
    int min_time = 100000, max_time = 0;
    vector <Job*> jobs;
    int status = read_file(file_name, jobs, min_time, max_time);
    if(status != OK){
        return status;
    }
    
    for(int i = 0; i < jobs.size() - 1; i++){
        json_output += jobs[i]->json_string();
        json_output += ",\n";
    }
    json_output += jobs[jobs.size() - 1]->json_string();
    json_output += "\n";
    
    
    json_output += "  ],\n  \n  \"title\" : \"\\\\textbf{";
    json_output += schedule_name;
    json_output += " scheduling";
    if(method != 0){
        json_output += " - method ";
        json_output += to_string(method);
    }
    json_output += "}\",\n";
    json_output += "  \"xlabel\": \"time\",\n";
    
    json_output += "  \"xticks\": "; // ToDo: scale it rightly
    int scale;
    if(max_time - min_time <= 50){
        scale = 2;
    }
    else if(max_time - min_time <= 100){
        scale = 5;
    }
    else{
        scale = 10;
    }
    string x_scale_string = "[";
    for(int i = min_time; i < max_time; i += scale){
        x_scale_string += to_string(i);
        x_scale_string += ", ";
    }
    x_scale_string += to_string(max_time);
    x_scale_string += "]";
    json_output += x_scale_string;
    json_output += "\n";
    
    json_output += "}";
    
    ofstream out("real_time_schedule.json", ios::out);
    if(!out.is_open()){
        cout << "Can't open the file " << "real_time_schedule.json" << endl;
        return FILE_OPEN_ERR;
    }
    out << json_output << endl;
    
    out.close();
    
    const char * val = ::getenv("GANTT_ADDR");
    if(val == 0)
        system("python3 ./gantt/runner.py&");
    else{
        string command;
        command = "python3 ";
        command += val;
        if(command[command.size() - 1] != '/')
            command += "/";
        command += "runner.py&";
        system(command.c_str());
    }
    
    system("sleep 3");
    
    return OK;
}

int main(int argc, char** argv) {
    
    if(argc != 2){
        cout << "Please specify the name of your algorithm\n";
        return ALGORITHM_NAME_NOT_SPECIFY_ERR;
    }
    
    int status;
    
    if(file_exist("scheduled_jobs.txt")){
        status = do_it_for_a_file(argv[1], "scheduled_jobs.txt");
    }
    else if(file_exist("scheduled_jobs1.txt")){
        int i = 0;
        while(true){
            i++;
            string name_of_file;
            name_of_file = "scheduled_jobs";
            name_of_file += to_string(i);
            name_of_file += ".txt";
            if(file_exist(name_of_file)){
                status = do_it_for_a_file(argv[1], name_of_file, i);
                if(status != OK){
                    return status;
                }
            }
            else{
                break;
            }
        }
    }
    else{
        cout << "There is no file called scheduled_jobs.txt or scheduled_jobs1.txt" << endl;
        return FILE_scheduled_jobs_DOES_NOT_EXIST;
    }
    
//    status = do_it_for_a_file(argv[1], "scheduled_jobs.txt");
    
//    system("sleep 10");
    system("rm -rf real_time_schedule.json");
    

    
    return status;
}

