#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
 
int exitFlag = 0;
int optionsEnable[4];
char* commands[4] = {"Process ID", "User ID", "CPU Usage", "Command"};

void Read() {
	FILE* file = fopen("/proc/top_procs/tops", "r");
	if(!file) {
		printf("FILE OPEN ERROR\n");
		return;
	}
	int i;
	char str[100], cmd[16];
	int pid, command, uid;
	float cpuusage;

	fscanf(file, "%s%d", str, &command);
	for(i = 0; i < 12; i++) {
		fscanf(file, "%s", str);
	}
	// fscanf(file, "%s%s%s%s%s%s", str, str, str, str, str, str);
	// printf("command is %s %d\n", str, command);
	for(i = 0; i < 50; i++)
		printf("-");
	printf("\n Row");
	for(i = 0; i < 4; i++) {
		if(optionsEnable[i]) {
			printf("%14s", commands[i]);
		}
	}
	printf("\n");
	for(i = 0; i < 15; i++) {
	// while(fscanf(file, "%d%d%f%s", &pid, &uid, &cpuusage, cmd) != EOF) {
		fscanf(file, "%d%d%f%s", &pid, &uid, &cpuusage, cmd);
		// printf("%3d: %7d | %7d | %f | %s\n", i+1, pid, uid, cpuusage, cmd);
		printf("%3d: ", i+1);
		if(optionsEnable[0])
			printf("%13d | ", pid);
		if(optionsEnable[1])
			printf("%13d | ", uid);
		if(optionsEnable[2])
			printf("%f | ", cpuusage);
		if(optionsEnable[3])
			printf("%15s", cmd);
		printf("\n");
	}
	for(i = 0; i < 50; i++)
		printf("-");
	printf("\n");
	fclose(file);
}
void* CallRead(void* argIn) {
	int *delay = (int*)argIn;
	while(!exitFlag) {
		// printf("Delay %d\n", *delay);
		sleep(*delay);
		Read();
	}
}

int main() {
	int period = 0, i = 0;
	printf("Please Enter The Period: ");
	scanf("%d", &period);
	
	char input;
	int options;
	printf("Which of these you want to observe?\n1.%s\t2.%s\t3.%s\t4.%s\n", commands[0], commands[1], commands[2], commands[3]);
	printf("Number of options to observe: ");
	scanf("%d", &options);
	printf("Now enter the number assigned to each option you want to observe\n");
	int tmp;
	for(i = 0; i < options; i++) {
		printf("- option %d:  ", i+1);
		scanf("%d", &tmp);
		optionsEnable[tmp-1] = 1;
	}
	pthread_t t1, t2;
	int* p = &period;
	int retval1 = pthread_create(&t1, NULL, &CallRead, p);
	int** ret;
	pthread_join(t1, (void**) ret);
	
	scanf("%c", &input);
	printf("input is %c\n", input);
	if(input == 'q') {
		exitFlag = 1;
	}
	return 0;
}

