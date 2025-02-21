#!/bin/bash  
while true; do  
    echo -e "AUTHENTICATE \"password\"\r\nSIGNAL NEWNYM\r\nQUIT" | nc 127.0.0.1 9051  
    sleep 30  
done  
