#!/bin/bash

REPO_DIR=$1
RESULTS_DIR=$2
NUM=0
DEFAULT=$(git -C $REPO_DIR rev-parse --abbrev-ref HEAD)

if [ ! -d $RESULTS_DIR/files ]; then
    mkdir $RESULTS_DIR/files
fi

while read LINE; do
    COMMITS=($LINE)
    LOCAL=${COMMITS[0]}
    REMOTE=${COMMITS[1]}
    MERGED=${COMMITS[2]}

    git -C $REPO_DIR checkout --force -b remote $REMOTE
    git -C $REPO_DIR checkout --force -b local $LOCAL
    BASE=$(git -C $REPO_DIR merge-base local remote)
    git -C $REPO_DIR merge remote > $RESULTS_DIR/merge.txt

    while read CONFLICT; do
	if [[ $CONFLICT =~ .*[[:space:]]([^\.]*\.py$) ]]; then
	    if [[ $CONFLICT == *"content"* ]]; then
		FILEPATH=$REPO_DIR/${BASH_REMATCH[1]}
		FILENAME=${FILEPATH##*/}
		NUM=$((NUM+1))

		cp $FILEPATH $RESULTS_DIR/files/
		mv $RESULTS_DIR/files/$FILENAME $RESULTS_DIR/files/${NUM}_${FILENAME%.py}_conflict.py
		
		git -C $REPO_DIR reset --merge
		
		cp $FILEPATH $RESULTS_DIR/files/
		mv $RESULTS_DIR/files/$FILENAME $RESULTS_DIR/files/${NUM}_${FILENAME%.py}_local.py
		
		git -C $REPO_DIR checkout remote
		
		cp $FILEPATH $RESULTS_DIR/files/
		mv $RESULTS_DIR/files/$FILENAME $RESULTS_DIR/files/${NUM}_${FILENAME%.py}_remote.py
		
		git -C $REPO_DIR checkout --force -b base $BASE
		
		cp $FILEPATH $RESULTS_DIR/files/
		mv $RESULTS_DIR/files/$FILENAME $RESULTS_DIR/files/${NUM}_${FILENAME%.py}_base.py
		
		git -C $REPO_DIR checkout --force -b merged $MERGED

		cp $FILEPATH $RESULTS_DIR/files/
		mv $RESULTS_DIR/files/$FILENAME $RESULTS_DIR/files/${NUM}_${FILENAME%.py}_expected.py
	    fi
	fi
    done <<< $(grep CONFLICT $RESULTS_DIR/merge.txt)

    git -C $REPO_DIR reset --merge
    git -C $REPO_DIR checkout $DEFAULT
    git -C $REPO_DIR branch -D local
    git -C $REPO_DIR branch -D remote
    git -C $REPO_DIR branch -D base
    git -C $REPO_DIR branch -D merged
    git -C $REPO_DIR reset --hard $DEFAULT

done < $RESULTS_DIR/merge_conflicts.txt
