#include <stdio.h>
#include <sys/socket.h>
#include <netdb.h>

#define BUFFER_SIZE 500
#define QUEUE_SIZE 5

#define throwError(msg) { fprintf(stderr, msg); exit(1); }

int main(int argc, char *argv[]) {
    int socketFD, connectionFD, clientId = 0;
    struct sockaddr_in server;

    unsigned char inputBuffer[BUFFER_SIZE];

    if (argc != 2) {
        fprintf(stderr, "Usage: %s port\n", argv[0]);
        exit(1);
    }

    if ((socketFD = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        throwError("socket creation failed\n");
    }

    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(atoi(argv[1]));

    if (bind(socketFD, (struct sockaddr *) &server, sizeof(server)) < 0) {
        throwError("port bind failed\n");
    }

    listen(socketFD, QUEUE_SIZE);

    printf("Waiting for transmision\n");
    while (1) {
        if ((connectionFD = accept(socketFD, (struct sockaddr *) 0, (socklen_t *) 0)) < 0) {
            throwError("connection accept failed\n");
        }

        if (fork() == 0) {
            close(socketFD);
            
            ssize_t dataLength;
            do {
                dataLength = read(connectionFD, inputBuffer, BUFFER_SIZE - 1);

                if (dataLength < 0) {
                    fprintf(stderr, "Packet receive failed\n");
                    continue;
                }

                if (dataLength > 0) {
                    inputBuffer[dataLength] = '\0';

                    printf("Received %zd bytes\n", dataLength);

                    if (dataLength < 6) {
                        printf("Message too short, dropping\n");
                        continue;
                    }

                    uint32_t messageId = inputBuffer[0] + (inputBuffer[1] << 8) + (inputBuffer[2] << 16) + (inputBuffer[3] << 24);
                    uint32_t messageLength = inputBuffer[4] + (inputBuffer[5] << 8);

                    printf("Message id: %u, length: %u\n", messageId, messageLength);
                    printf("Start of payload: %.*s...\n", 10, inputBuffer+6);
                }
            } while (dataLength > 0);

            exit(1);
        }

        close(connectionFD);
    }
}
