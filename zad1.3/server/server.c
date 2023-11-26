#include <stdio.h>
#include <sys/socket.h>
#include <netdb.h>

#define BUFFER_SIZE 500

#define throwError(msg) { fprintf(stderr, msg); exit(1); }

int main(int argc, char *argv[]) {
    int socketFD;

    struct sockaddr_in server;
    struct sockaddr_storage peerAddress;

    unsigned char inputBuffer[BUFFER_SIZE];
    unsigned char response[5];

    uint32_t previousMessageId = 0;

    if (argc != 2) {
        fprintf(stderr, "Usage: %s port\n", argv[0]);
        exit(1);
    }

    if ((socketFD = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        throwError("socket creation failed\n");
    }

    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(atoi(argv[1]));

    if (bind(socketFD, (struct sockaddr *) &server, sizeof(server)) < 0) {
        throwError("port bind failed\n");
    }

    printf("Waiting for transmision\n");
    while (1) {
        socklen_t peerAddressLen = sizeof(peerAddress);

        ssize_t dataLength = recvfrom(socketFD, inputBuffer, BUFFER_SIZE - 1, 0, 
            (struct sockaddr *) &peerAddress, &peerAddressLen);

        if (dataLength < 0) {
            fprintf(stderr, "Packet receive failed\n");
            continue;
        }

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

        response[0] = inputBuffer[0];
        response[1] = inputBuffer[1];
        response[2] = inputBuffer[2];
        response[3] = inputBuffer[3];
        response[4] = 0;

        if (messageLength + 6 != dataLength){
            printf("Incorrect message length\n");
            response[4] = 1;
        }
        if (previousMessageId + 1 < messageId){
            printf("Incorrect message id\n");
            response[4] = 1;
        }

        if (sendto(socketFD, response, sizeof(response), 0, 
            (struct sockaddr *) &peerAddress, peerAddressLen) < 0) {

            printf("Failed to send response\n");
        }

        if (messageId == previousMessageId + 1) {
            previousMessageId = messageId;
        }
    }
}
