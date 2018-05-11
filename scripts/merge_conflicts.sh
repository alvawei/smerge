#!/bin/bash

if [  ]; then
    echo "Usage: ./merge_conflicts <Repository directory> <Results directory>"
else
    REPO_DIR=$1
    RESULTS_DIR=$2
    NUM=0
    GET_FILES=0;

    touch $RESULTS_DIR/result.txt
    rm $RESULTS_DIR/result.txt
    touch $RESULTS_DIR/result.txt
    
    while read line; do
	COMMITS=($line)
        LOCAL=${COMMITS[0]}
	REMOTE=${COMMITS[1]}
	MERGED=${COMMITS[2]}
	
	git -C $REPO_DIR checkout --force -b remote $REMOTE
 	git -C $REPO_DIR checkout --force -b local $LOCAL
	#BASE=$(git -C $REPO_DIR merge-base local remote)
	git -C $REPO_DIR merge remote > $RESULTS_DIR/merge.txt
	
	while read conflict; do
	    if [[ $conflict =~ .*[[:space:]]([^\.]*\.py) ]]; then
		if [[ $conflict == *"content"* ]]; then
		    FILEPATH=$REPO_DIR/${BASH_REMATCH[1]}
		    FILENAME=${FILEPATH##*/}
		    NUM=$((NUM+1))
		    
		    if [ ! -d $RESULTS_DIR/conflicts ]; then
			mkdir $RESULTS_DIR/conflicts
		    fi
		    
		    if [ $GET_FILES -eq 1 ]; then
			# get copies of base local remote and conflict
			cp $FILEPATH $RESULTS_DIR/
			mv $RESULTS_DIR/$FILENAME $RESULTS_DIR/conflicts/${NUM}_${FILENAME%.py}_conflict.py
			
			git -C $REPO_DIR reset --merge
			
			cp $FILEPATH $RESULTS_DIR/
			mv $RESULTS_DIR/$FILENAME $RESULTS_DIR/conflicts/${NUM}_${FILENAME%.py}_local.py
			
			git -C $REPO_DIR checkout remote
			
			cp $FILEPATH $RESULTS_DIR/
			mv $RESULTS_DIR/$FILENAME $RESULTS_DIR/conflicts/${NUM}_${FILENAME%.py}_remote.py
			
			git -C $REPO_DIR checkout --force -b base $BASE
			
			cp $FILEPATH $RESULTS_DIR/
			mv $RESULTS_DIR/$FILENAME $RESULTS_DIR/conflicts/${NUM}_${FILENAME%.py}_base.py
		    else
			# try to resolve conflict using our mergetool
			RESULT="$(yes | git -C ${REPO_DIR} mergetool --tool=smerge $FILEPATH)"
			
			if [[ $RESULT =~ *SUCCESS* ]]; then
			    echo "SUCCESS" >> $RESULTS_DIR/result.txt

			    cp $FILEPATH $RESULTS_DIR/
			    mv $RESULTS_DIR/$FILENAME $RESULTS_DIR/conflicts/${NUM}_${FILENAME%.py}_actual.py
			 
			else
			    echo "FAILURE" >> $RESULTS_DIR/result.txt
			fi
			
			git -C $REPO_DIR reset --merge

		    fi
		    
		    # get the human merged file
		    git -C $REPO_DIR checkout --force -b merged $MERGED

		    cp $FILEPATH $RESULTS_DIR/
		    mv $RESULTS_DIR/$FILENAME $RESULTS_DIR/conflicts/${NUM}_${FILENAME%.py}_expected.py

		fi
	    fi
	done <<< $(grep CONFLICT $RESULTS_DIR/merge.txt)

	git -C $REPO_DIR reset --merge			
	git -C $REPO_DIR checkout master
	if [ $GET_FILES -eq 1 ]; then
	    git -C $REPO_DIR branch -D base
	fi
	git -C $REPO_DIR branch -D local
	git -C $REPO_DIR branch -D remote
	git -C $REPO_DIR branch -D merged
	git -C $REPO_DIR reset --hard master

    done < $RESULTS_DIR/merge_conflicts.txt
fi
