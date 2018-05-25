#!/bin/bash

if [ ! -d test_results ]; then
    mkdir test_results
fi

# create a final table with all of the csv's included
echo "Repo,Conflicts,Modified,Unresolved,%Modified,%Unresolved" > table.csv

cat repos.txt | while read line; do
    REPO_NAME=$(echo $line | cut -d '/' -f 5)
    CUR_DIR=$(pwd)
    cd /tmp/
    git clone $line.git
    cd $CUR_DIR
    ./test_repo.sh $REPO_NAME
    sed '2q;d' ${REPO_NAME}.csv >> table.csv
done
