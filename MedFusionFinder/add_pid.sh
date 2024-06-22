#!/bin/bash

# Define the list of PIDs to check
pids_to_check=("5275857714" "5900350716" "5936292207" "6090981279" "6262348655" "6286728939" "6303994710" "7451555234" "9111763980" "9640476770")

# File containing unique PIDs
unique_pids_file="uniq_pids.txt"

# Extract unique PIDs from the CSV file and save them to a temporary file
awk -F',' 'NR>1 {print $1}' pid_pathologies.csv | sort -u > $unique_pids_file

# Check each PID in pids_to_check and add if not present
for pid in "${pids_to_check[@]}"; do
  if grep -q "^$pid$" $unique_pids_file; then
    echo "PID $pid already exists in $unique_pids_file"
  else
    echo "PID $pid not found in $unique_pids_file. Adding it."
    echo $pid >> $unique_pids_file
  fi
done

# Sort the file again to maintain order and remove any accidental duplicates
sort -u $unique_pids_file -o $unique_pids_file

echo "Updated $unique_pids_file:"
cat $unique_pids_file

