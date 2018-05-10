#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: ./test_repo.sh <Repository name>"
else
    REPO_NAME=$1
    REPO_DIR=/tmp/${REPO_NAME}
    RESULTS_DIR=test_results/${REPO_NAME}_test_results
    
    # create a directory to store this repo's data
    if [ ! -d ${RESULTS_DIR} ]; then
	mkdir ${RESULTS_DIR}
    fi
    
    # Find all merge conflicts for the given repo
    if [ ! -f merge_conflicts/${REPO_NAME}_merge_conflicts.txt ]; then
	./find_conflicts.sh ${REPO_DIR} ${RESULTS_DIR}
	cp ${RESULTS_DIR}/merge_conflicts.txt merge_conflicts
	mv merge_conflicts/merge_conflicts.txt merge_conflicts/${REPO_NAME}_merge_conflicts.txt 
    else
	cp merge_conflicts/${REPO_NAME}_merge_conflicts.txt ${RESULTS_DIR}
	mv  ${RESULTS_DIR}/${REPO_NAME}_merge_conflicts.txt ${RESULTS_DIR}/merge_conflicts.txt 
    fi
    
    ./merge_conflicts.sh ${REPO_DIR} ${RESULTS_DIR}
    
    ./run_diff.sh ${RESULTS_DIR}

    # Output <repositoryname>.csv file
#    ./make_csv.sh ${REPO_NAME} ${RESULTS_DIR} $3
fi
