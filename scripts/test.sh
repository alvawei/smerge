#!/bin/bash

# This script goes through the repository list in repos.txt, and
# Runs test_repo.sh on each repository and records the final result 


# create test_result folder if it doesn't already exist
if [ ! -d test_results ]; then
    mkdir test_results
fi

# create a final table
echo "Repo,Conflicts,Modified,Unresolved,%Modified,%Unresolved" > table.csv

# go through repository list, and for each repository
# clone the repository and run test_repo.sh
# add result back to the final table
cat repos.txt | while read line; do
    REPO_NAME=$(echo $line | cut -d '/' -f 5)
    CUR_DIR=$(pwd)

    cd /tmp/
    git clone $line.git
    cd $CUR_DIR

    ./test_repo.sh $REPO_NAME

    sed '2q;d' ${REPO_NAME}.csv >> table.csv
done
