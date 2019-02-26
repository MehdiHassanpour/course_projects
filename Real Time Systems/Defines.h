/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   Defines.h
 * Author: shahrooz
 *
 * Created on February 7, 2019, 8:39 PM
 */

#ifndef DEFINES_H
#define DEFINES_H

#ifdef __cplusplus
extern "C" {
#endif

#define MAX_NUMBER_OF_JOBS  1000

#define MAX_NUMBER_OF_START_TIMES_PER_JOB  1000

    
// errors
#define OK                                   0
#define FILE_OPEN_ERR                       -1
#define ALGORITHM_NAME_NOT_SPECIFY_ERR      -2
#define FILE_scheduled_jobs_DOES_NOT_EXIST  -3

    
#ifdef __cplusplus
}
#endif

#endif /* DEFINES_H */

