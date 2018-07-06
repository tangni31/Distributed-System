all:
	gcc -o client client.c timeServer_clnt.c -lnsl
	gcc -o server -DRPC_SVC_FG server.c timeServer_svc.c -lnsl
clean:
	rm -f client client.o server server.o clnt.o svc.o
