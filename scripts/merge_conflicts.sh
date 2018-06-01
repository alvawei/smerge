#!/bin/bash

# This script goes through the merge_conflicts.txt for the given repository, 
# merge the branches using 'git merge' command to generate merge conflict, and
# try to resolve it using smerge as mergetool.
# It stores conflict file from running 'git merge' as <filename>_conflict.py
# smerge result as <filename>_actual.py
# human resolution as <filename>_expected.py

if [ $# -ne 2 ]; then
    echo "Usage: ./merge_conflicts <Repository directory> <Results directory>"
else
    # Initialization
    REPO_DIR=$1
    RESULTS_DIR=$2
    NUM=0

    touch $RESULTS_DIR/result.txt
    rm $RESULTS_DIR/result.txt
    touch $RESULTS_DIR/result.txt

    DEFAULT_BRANCH=$(git -C $1 rev-parse --abbrev-ref HEAD)    

    if [ ! -d $RESULTS_DIR/conflicts ]; then
	mkdir $RESULTS_DIR/conflicts
    fi

    # for each merge conflict found
    # Merge local and remote, and try smerge to resolve the conflict
    # Save the conflicted file as 'conflict', human resolution as 'expected', and smerge result as 'actual'
    while read line; do
	COMMITS=($line)
        LOCAL=${COMMITS[0]}
	REMOTE=${COMMITS[1]}
	MERGED=${COMMITS[2]}
	
	git -C $REPO_DIR checkout --force -b remote $REMOTE
 	git -C $REPO_DIR checkout --force -b local $LOCAL
	git -C $REPO_DIR merge remote > $RESULTS_DIR/merge.txt

	# Read git merge result, and
	# Try smerge on a content conflict in .py file
	while read conflict; do
	    if [[ $conflict =~ .*[[:space:]]([^\.]*\.py$) ]]; then
		if [[ $conflict == *"content"* ]]; then
		    FILEPATH=$REPO_DIR/${BASH_REMATCH[1]}
		    FILENAME=${FILEPATH##*/}
		    NUM=$((NUM+1))
		    
		    cp $FILEPATH $RESULTS_DIR/
		    mv $RESULTS_DIR/$FILENAME $RESULTS_DIR/conflicts/${NUM}_${FILENAME%.py}_conflict.py
		    
		    
		    # try to resolve conflict using smerge as mergetool
		    echo "$(yes | git -C ${REPO_DIR} mergetool --tool=smerge $FILEPATH)" > $RESULTS_DIR/mergetool.txt
		    while read mergetool_result; do
			if [[ $mergetool_result =~ .*resolved:[[:space:]](.*)/(.*) ]]; then
			    
			    cp $FILEPATH $RESULTS_DIR/
			    mv $RESULTS_DIR/$FILENAME $RESULTS_DIR/conflicts/${NUM}_${FILENAME%.py}_actual.py
			  
			    SUCCESS=${BASH_REMATCH[1]}
			    TOTAL=${BASH_REMATCH[2]}

			    if [ $TOTAL -eq 0 ]; then
			        TOTAL=$(grep '<<< HEAD' $RESULTS_DIR/conflicts/${NUM}_${FILENAME%.py}_conflict.py | wc -l)
				SUCCESS=$TOTAL
			    fi

			    echo "$NUM $SUCCESS/$TOTAL" >> $RESULTS_DIR/result.txt
			fi
		    done <<< $(grep resolved $RESULTS_DIR/mergetool.txt)
		    
		    git -C $REPO_DIR reset --merge
		    
		fi
		
		# get the human merged file
		git -C $REPO_DIR checkout --force -b merged $MERGED
		
		cp $FILEPATH $RESULTS_DIR/
		mv $RESULTS_DIR/$FILENAME $RESULTS_DIR/conflicts/${NUM}_${FILENAME%.py}_expected.py
		
	    fi
	done <<< $(grep CONFLICT $RESULTS_DIR/merge.txt)

	# clean up branches for next run
	git -C $REPO_DIR reset --merge			
	git -C $REPO_DIR checkout $DEFAULT_BRANCH
	git -C $REPO_DIR branch -D local
	git -C $REPO_DIR branch -D remote
	git -C $REPO_DIR branch -D merged
	git -C $REPO_DIR reset --hard $DEFAULT_BRANCH

    done < $RESULTS_DIR/merge_conflicts.txt
fi
