#!/bin/sh
/usr/bin/docker-entrypoint.sh server /data --console-address ":9001" &
sleep 5
mc alias set myminio http://localhost:9000 testuser testpass
mc mb myminio/test-bucket
mc anonymous set public myminio/test-bucket
wait