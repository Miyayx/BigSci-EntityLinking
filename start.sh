#!/bin/bash
screen -LS termextraction wine /mnt/wind/tsinghua/BigSci/code/term/bin/termextracttools.exe
screen -LS entitylinking python webserver.py
    

