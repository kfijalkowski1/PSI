#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define TRUE 1
#define BSIZE 1024

#define bailout(s) {perror(s); exit(1); }
#define notDone() TRUE

#define DEF_PORT "8000"

int moreWork(void) {
    return 1;
}

int  main(int argc, char **argv) {
    int sock, msgsock, rval, ListenQueueSize=5;
    socklen_t length;
    struct addrinfo *bindto_address;
    struct addrinfo hints;
    struct sockaddr_in server;
    char buf[BSIZE];


    /* initialize socket type, address and port */
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;
    if ( getaddrinfo(0, DEF_PORT, &hints, &bindto_address) != 0 ) 
        bailout("getting local address");

    sock = socket(bindto_address->ai_family, bindto_address->ai_socktype, bindto_address->ai_protocol);
    if (sock == -1) 
        bailout("opening stream socket");

    /* dowiaz adres do gniazda */
    if (bind(sock, bindto_address->ai_addr, bindto_address->ai_addrlen )
            == -1) 
        bailout("binding stream socket");
    freeaddrinfo(bindto_address);

    /* zacznij przyjmowaæ polaczenia... */
    listen(sock, ListenQueueSize);

    do {
        msgsock = accept(sock,(struct sockaddr *) 0, (socklen_t *) 0);
        if (msgsock == -1 ) {
            bailout("accept"); 
	} else do {
                memset(buf, 0, sizeof buf);
                if ((rval = read(msgsock,buf, BSIZE)) == -1)
                    bailout("reading stream message");
                if (rval == 0)
                    printf("%s: Ending connection\n", argv[0]);
                else
                    printf("%s: -->%s\n", argv[0], buf);
            } while (rval != 0);
        close(msgsock);
        fflush( stdout );
    } while( moreWork() );
    /*
     * gniazdo sock nie zostanie nigdy zamkniete jawnie,
     * jednak wszystkie deskryptory zostana zamkniete gdy proces
     * zostanie zakonczony (np w wyniku wystapienia sygnalu)
     */

    exit(0);
}