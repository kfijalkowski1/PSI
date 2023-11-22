#!/bin/sh

docker run -it --rm --network-alias z26_z11_server --hostname z26_z11_server --network z26_network --name z26_z11_server z26_z11_server_image /server/server 8000
