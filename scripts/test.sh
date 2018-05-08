#!/bin/bash

if [ ! -d repos ]; then
    mkdir repos
fi

if [ ! -d test_results ]; then
    mkdir test_results
fi

cat repos.txt | while read line; do
    REPO_NAME=$(echo $line | cut -d '/' -f 5)
    cd repos
    git clone $line.git
    cd ..
    ./test_repo.sh $REPO_NAME
done

