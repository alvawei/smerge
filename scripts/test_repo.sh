#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: ./test_repo.sh <Repository name>"
else
    REPO_NAME=$1
    REPO_DIR=repos/${REPO_NAME}
    RESULTS_DIR=test_results/${REPO_NAME}_test_results
    
    # create a directory to store this repo's data
    if [ ! -d ${RESULTS_DIR} ]; then
	mkdir ${RESULTS_DIR}
    fi
    
    # Find all merge conflicts for the given repo
    ./find_conflicts.sh ${REPO_DIR} ${RESULTS_DIR}
    
    # Run Conflerge w/ trees on found conflicts in the repo
#    if [ ! -f ${RESULTS_DIR}/res.txt ]; then
#	./merge_conflicts.sh ${REPO_DIR} ${RESULTS_DIR} $3 > ${RESULTS_DIR}/res.txt
#    fi
    
    # Output <repositoryname>.csv file
#    ./make_csv.sh ${REPO_NAME} ${RESULTS_DIR} $3
fi
