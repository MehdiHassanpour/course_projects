/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Job.h
 * Author: shahrooz
 *
 * Created on February 7, 2019, 8:35 PM
 */

#ifndef JOB_H
#define JOB_H

#include "Defines.h"
#include <vector>
#include <string>
#include <cstdlib>

using namespace std;

class Job {
public:
    Job(string &name);
    Job(const Job& orig) = delete;
    virtual ~Job();
    
    string json_string();
    void set_number(int number);
    
//    static int color_number;

    int arrival_time;
    int deadline;
    int computation_time;
    int finish_time;
    vector <int> start_time;
    vector <int> comp_per_start;

private:
    string color;
    string name;
    int number;

};

#endif /* JOB_H */

