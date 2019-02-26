#include <arpa/inet.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <netinet/in.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <pthread.h>


#define SERVER_LISTENING_PORT 1234

int closeSocket = 0;
int clientClose = 0;

void* srv_send(void* Socket);
void* srv_recv(void* Socket);
void handle_client(char*, int);

int main(int argc, char ** argv)
{

    if(argc <= 1) {
        // server mode
        fprintf(stderr, "im server...\n");
        /* TODO
         * socket()
         * bind()
         * listen()
         * accept()*/
        struct sockaddr_in my_addr;
        struct sockaddr_in clinet_addr;
        int mysocket = socket(AF_INET, SOCK_STREAM, 0);
        int new_socket;
        int* server_send_return, server_recv_return;
        if(mysocket == -1) { //error
            fprintf(stderr, "error in creating socket\n");
        }else {
            my_addr.sin_family = AF_INET;
            my_addr.sin_port = htons(SERVER_LISTENING_PORT);
            // my_addr.sin_addr.s_addr = INADDR_ANY;
            my_addr.sin_addr.s_addr = inet_addr("0.0.0.0");
            memset(&(my_addr.sin_zero), '\0', 8);
            socklen_t sin_size;
            pthread_t server_send_thread, server_recv_thread;
            if(bind(mysocket, (struct sockaddr*) &my_addr, sizeof(struct sockaddr)) != -1) {
                if(listen(mysocket, 1) != -1) {
                    while(true) {
                        sin_size = sizeof(struct sockaddr_in);
                        if((new_socket = accept(mysocket, (struct sockaddr*) &clinet_addr, &sin_size)) != -1) {
                            fprintf(stderr, "Accepted, threads to read or write enabled\n");
                            closeSocket = 0;
                            if(!pthread_create(&server_send_thread, NULL, srv_send, &new_socket)) {
                            }else {
                                fprintf(stderr, "%s\n", "error creating thread, server send");
                            }
                            if(!pthread_create(&server_recv_thread, NULL, srv_recv, &new_socket)) {

                            }else {
                                fprintf(stderr, "%s\n", "error creating thread, server send");
                            }
                            if(closeSocket == 1) {
                                fprintf(stderr, "%s\n", "closing connection");
                                close(new_socket);
//                                pthread_kill(server_send_thread, SIGKILL);
                                pthread_cancel(server_send_thread);
                                pthread_cancel(server_recv_thread);
                            }
//                            pthread_join(server_recv_thread, NULL/*&server_recv_return*/);
//                            pthread_join(server_send_thread, NULL/*&server_send_return*/);
                        }else {
                            //error in accepting
                        }
                    }
                }else {
                    //error in listening
                    fprintf(stderr, "error in listening");
                }
            }else {
                //error in binding
                fprintf(stderr, "error in binding\n");
            }
        }
    } //end of server
    else if(argc == 3) {
        // client mode
        fprintf(stderr, "%s\n", "im client...");
        int port = atoi(argv[2]);
        handle_client(argv[1], port);
    }
    else {
        // error
        printf("Unknown argument\n");
        fflush(stdout);
    }
}


void* srv_send(void* Socket) {
    int socket = *((int*)Socket);
    char* buffer = (char*) malloc(1024*(sizeof(char)));
    int length = 1024, bytes_sent = 0, onetime_bytes_sent;
    int *ret_value = (int*)malloc(sizeof(int));
//    pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL);
    while(!closeSocket) {
        if(fgets(buffer, 1023, stdin) != NULL) {
            fprintf(stderr, "buffer is: %s", buffer);
            do {
                onetime_bytes_sent = send(socket, (void *) (buffer + bytes_sent), strlen(buffer) - bytes_sent, 0);
                if (onetime_bytes_sent == -1) {
                    fprintf(stderr, "%s\n", "error in sending message");
                    *ret_value = -1;
                    return (void *) (ret_value);
                }
                bytes_sent += onetime_bytes_sent;
            } while (bytes_sent < (int) strlen(buffer));
            bytes_sent = 0;
        }else {
            clientClose = 1;
            close(socket);
        }
    }
    *ret_value = bytes_sent;
    return (void*)(ret_value);
}

void* srv_recv(void* Socket) {
    int socket = *((int*)Socket);
    char* buffer;
    int buffer_size = 1024;
    unsigned int flags = 0;
    int bytes_recved = 0;
    while(!closeSocket) {
        buffer = (char*)malloc(sizeof(char)*1024);
        bytes_recved = recv(socket, (void*) buffer, buffer_size, flags);
        if(bytes_recved == 0) {
            //closed connection
            fprintf(stderr, "%s\n", "Connection Closed");
            closeSocket = 1;
        }else if(bytes_recved == -1) {
            //error receiving
            fprintf(stderr, "%s\n", "error receiving client message");
        } else {
            int i = 0;
            for(; i < 1024; i++) {
                if(buffer[i] == EOF) {
                    fprintf(stderr, "%s\n", "End Of File seen");
                    closeSocket = 1;
                }
            }
            if(!closeSocket) {
                printf("%s", buffer);
                fflush(stdout);
            }
            memset(buffer, 0, 1024);
            free(buffer);
        }
    }
    return NULL;
}

void handle_client(char* ip, int port) {
    int mysocket;
    struct sockaddr_in serverAddr;
    socklen_t addr_size;
    pthread_t client_send_thread, client_recv_thread;
    mysocket = socket(AF_INET, SOCK_STREAM, 0);

    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    serverAddr.sin_addr.s_addr = inet_addr(ip);
    memset(serverAddr.sin_zero, '\0', sizeof serverAddr.sin_zero);

    addr_size = sizeof(serverAddr);
    if(connect(mysocket, (struct sockaddr *) &serverAddr, addr_size) == -1) {
        printf("CAN'T CONNECT");
        fflush(stdout);
        return;
    }
    pthread_create(&client_recv_thread, NULL, srv_recv, &mysocket);
    pthread_create(&client_send_thread, NULL, srv_send, &mysocket);
    while(true) {
        if(clientClose == 1) {
            closeSocket = 1;
        }
        if(closeSocket == 1) {
            fprintf(stderr, "%s\n", "client closing socket");
            close(mysocket);
            pthread_cancel(client_send_thread);
            pthread_cancel(client_recv_thread);
//            pthread_join(client_recv_thread, NULL);
//            pthread_join(client_send_thread, NULL);
            return;
        }
    }
}
