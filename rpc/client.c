#include "timeServer.h"
#include <rpc/rpc.h>
#include<time.h>

int
main(int argc, char *argv[]){
    char *server;
    CLIENT *clnt;
    long *result;
    char time_buffer[32];
    char *timeserver_1_arg;

    if (argc<2){
	fprintf(stderr,"usage: %s host\n", argv[0]);
	exit(1);
    }
    server = argv[1];
    /*Create client handle*/
    clnt = clnt_create(server, TIME_PROG, TIMESERVER_VERS, "udp");  
    if (clnt == NULL){
	clnt_pcreateerror(server); /*Couldn’t establish connection with server. Print error message and die.*/
	exit(1);
    }
    /*Call the remote procedure on server*/
    result = get_time_1((void*)&timeserver_1_arg, clnt);
    if(result == (long *) NULL){ /*An error occurred while calling the server*/
	clnt_perror(clnt, "call server failed");
	exit(1);
    }
    else{
	strftime(time_buffer, 32,"%F %T", localtime(result));
        printf("Time is %s\n", time_buffer);
    }
    clnt_destroy (clnt);
    exit(0);
}
