#!/bin/bash
INPUT_DIR="./"
OUTPUT_DIR="./"
for input in `ls | tr '\n' '\n'`
do
    output="$input"
    echo "$INPUT_DIR$input output to $OUTPUT_DIR$output"
    ant mapping $INPUT_DIR$input $OUTPUT_DIR$output
done
