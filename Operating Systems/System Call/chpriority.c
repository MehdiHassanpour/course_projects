#define _GNU_SOURCE

#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <sys/syscall.h>
#include <string.h>
#include <stdlib.h>
#include <sched.h>
#include <sys/resource.h>
#include <sys/wait.h>


void matrixMult();
void monitor(id_t id,int x);
void printStart_Compeletion(int s,id_t id);

int main() {
	pid_t pid1, pid2;
	int which = PRIO_PROCESS;

	printf("Enter the change value : ");
	long value;
	scanf("%ld" , &value);

	pid1 = fork();
	if(pid1 < 0) {
		printf("Error occurred in creating process1\n");	
	}
	else if(pid1 > 0) {
		pid2 = fork();
		if(pid2 < 0) {
			printf("Error occurred in creating process1\n");	
		}
		else if(pid2 == 0) {
			id_t id2 = getpid();
			//printf("=================================> child2 Priority : %d\n", getpriority(which, id2));

			printStart_Compeletion(1,id2);
			matrixMult();	
			printStart_Compeletion(0,id2);
		}
		else if(pid2 > 0) {
			printf("*************CHILD1 PID =  %d, CHILD2 PID = %d*****************\n", pid1, pid2);
			printf("checking error in syscall %ld\n",syscall(327, pid1, pid2, value));
			waitpid(pid1, NULL, 0);
			waitpid(pid2, NULL, 0);
		}
	}
	else {
		id_t id1 = getpid();
		//printf("=================================> child1 Priority : %d\n", getpriority(which, id1));

		printStart_Compeletion(1,id1);
		matrixMult();
		printStart_Compeletion(0,id1);
	}
	return 0;
}

void matrixMult() {
	int matrix1[4][4] = {{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 3, 5, -2}, {0, -4, 1, 1}};
	int matrix2[4][4] = {{0, 1, 2, 3}, {5, 0, 1, 8}, {0, 1, 2, -1}, {-1, -2, 5, 3}};
	int result [4][4];
	int i, j, k;
	id_t id = getpid();
	for(i = 0; i < 4; i++){
		for(j = 0; j < 4; j++){
			result[i][j] = 0;
		}
	}
	for (i = 0; i < 100; i++) {
		for(j = 0; j < 100; j++) {
			for(k = 0; k < 100; k++) {
				result[i%4][j%4] += (matrix1[i%4][k%4]*matrix2[k%4][j%4]);
			}
		}
		if(i%10 == 0) {
			monitor(id,i);
		}
	}
}

void monitor(id_t id,int x){
	if(id%2 == 0){
		printf("%2d: ",x);
		int i;
		for(i=0;i<10;i++){
			if(10*i <= x)
				printf("####");
			else
				printf("    ");
		}
		printf("\n"); 
	}
	else{
		printf("\t\t\t\t\t\t\t%2d: ",x);
		int i;
		for(i=0;i<10;i++){
			if(10*i <= x)
				printf("####");
			else
				printf("    ");
		}
		printf("\n"); 	
	}
}

void printStart_Compeletion(int s,id_t id){
	if(s){
		if(id%2 == 0){
			printf("\n*************CHILD %d STARTED*************\n\n",id);
			printf("PROGRESS BAR :\n");
		}
		else{
			printf("\n\t\t\t\t\t\t\t*************CHILD %d STARTED*************\n\n",id);
			printf("\t\t\t\t\t\t\tPROGRESS BAR :\n");
		}
	}
	else{
		if(id%2 == 0)
			printf("\n*************THIS CHILD FINISHED************\n\n");
		else
			printf("\n\t\t\t\t\t\t\t*************THIS CHILD FINISHED************\n\n");
	}
}
