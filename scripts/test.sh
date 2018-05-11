#!/bin/bash

if [ ! -d test_results ]; then
    mkdir test_results
fi

cat repos.txt | while read line; do
    REPO_NAME=$(echo $line | cut -d '/' -f 5)
    CUR_DIR=$(pwd)
    cd /tmp/
    git clone $line.git
    cd $CUR_DIR
    ./test_repo.sh $REPO_NAME
done

