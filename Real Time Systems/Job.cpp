/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Job.cpp
 * Author: shahrooz
 * 
 * Created on February 7, 2019, 8:35 PM
 */

#include "Job.h"

string colors[] = {"black", "blue", "brown", "cyan", "darkgray", "gray",
        "green", "lightgray", "lime", "magenta", "olive", "orange", "pink",
        "purple", "red", "teal", "violet", "yellow"};

Job::Job(string &name) {
//    this->color = colors[color_number % 18];
//    color_number++;
    this->name = name;
}

Job::~Job() {
}

//int Job::color_number = 13;

void Job::set_number(int number){
    this->number = number;
    this->name += to_string(number);
    
    this->color = colors[(number + 12) % 18];
    
    return;
}

string Job::json_string(){
    
    string ret;
    
    char temp[100];
    
    if(start_time.size() == 1){
        ret = "    {\n";

        ret += "      \"label\": \"";
        ret += this->name;
        ret += "\",\n";
        
        ret += "      \"start\": ";
        ret += to_string(this->start_time[0]);
        ret += ",\n";
        
        ret += "      \"end\": ";
        ret += to_string(this->finish_time);
        ret += ",\n";
        
        ret += "      \"milestones\": [";
        ret += to_string(this->arrival_time);
        ret += ", ";
        ret += to_string(this->deadline);
        ret += "],\n";
        
        ret += "      \"color\": \"";
        ret += this->color;
        ret += "\"\n";

        ret += "    }";
    }
    else{
        for(int i = 0 ; i < start_time.size(); i++){
            ret += "    {\n";
            
            ret += "      \"label\": \"";
            ret += this->name;
            ret += " - ";
            ret += to_string(i + 1);
            ret += "\",\n";

            ret += "      \"start\": ";
            ret += to_string(this->start_time[i]);
            ret += ",\n";

            ret += "      \"end\": ";
            ret += to_string(this->start_time[i] + this->comp_per_start[i]);
            ret += ",\n";

            ret += "      \"milestones\": [";
            ret += to_string(this->arrival_time);
            ret += ", ";
            ret += to_string(this->deadline);
            ret += "],\n";

            ret += "      \"color\": \"";
            ret += this->color;
            ret += "\"\n";
            
            if(i == start_time.size() - 1){
                ret += "    }";
            }
            else{
                ret += "    },\n";
            }
        }
    }
    
    return ret;
}
