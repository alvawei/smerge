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
    
    # create a final table with all of the csv's included
    echo "Repo,Conflicts,Unresolved,Correct,CorrectNC,Incorrect,%Correct,%CorrectCW,%Unresolved,%Incorrect" > table.csv
    cat *.csv > table.csv
done

