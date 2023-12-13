#!/bin/sh

docker run -it --rm --network-alias z26_z22_server --hostname z26_z22_server --network z26_network --name z26_z22_server z26_z22_server_image /server/server 8000
