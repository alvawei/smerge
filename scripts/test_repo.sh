#!/bin/bash

# This script invokes other scripts to test smerge on the given repository, and
# record the result into a csv file

if [ $# -ne 1 ]; then
    echo "Usage: ./test_repo.sh <Repository name>"
else
    REPO_NAME=$1
    REPO_DIR=/tmp/${REPO_NAME}
    RESULTS_DIR=test_results/${REPO_NAME}_test_results
    
    # create a directory inside test_result for this repository
    if [ ! -d ${RESULTS_DIR} ]; then
	mkdir ${RESULTS_DIR}
    fi
    
    # Find all merge conflicts for the given repo
    # Check merge_conflicts folder to grab the list of conflicts from previous run
    # Run find_conflicts.sh if it doesn't exist
    if [ ! -f merge_conflicts/${REPO_NAME}_merge_conflicts.txt ]; then
	./find_conflicts.sh ${REPO_DIR} ${RESULTS_DIR}
	cp ${RESULTS_DIR}/merge_conflicts.txt merge_conflicts
	mv merge_conflicts/merge_conflicts.txt merge_conflicts/${REPO_NAME}_merge_conflicts.txt 
    else
	cp merge_conflicts/${REPO_NAME}_merge_conflicts.txt ${RESULTS_DIR}
	mv  ${RESULTS_DIR}/${REPO_NAME}_merge_conflicts.txt ${RESULTS_DIR}/merge_conflicts.txt 
    fi
    
    # Enable to grab base, local, remote files for testing purpose
    # ./get_files.sh ${REPO_DIR} ${RESULTS_DIR}
    
    # Run merge_conflicts.sh to see how smerge performs on the given repository
    ./merge_conflicts.sh ${REPO_DIR} ${RESULTS_DIR}

    # Output results in <repositoryname>.csv file
    ./make_csv.sh ${REPO_NAME} ${RESULTS_DIR}
fi
