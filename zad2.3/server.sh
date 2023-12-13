#!/bin/sh

docker run -it --rm --network-alias z26_z23_server --hostname z26_z23_server --network z26_network --name z26_z23_server z26_z23_server_image /server/server 8000
