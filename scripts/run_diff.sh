#!/bin/bash

pushd $1
for FILE in `ls *_actual.py`; do
    FILENAME=${FILE::-10}
    F1=${FILENAME}_actual.py
    F2=${FILENAME}_expected.py
    DIFF=${FILENAME}_.out
    DIFF_NC=${FILENAME}_nc.out

    # compare actual merge and expected merge
    diff $F1 $F2 > $DIFF

    if [ -s $DIFF ];then
	RESULT="FAILURE"
    else
	RESULT="SUCCESS"
    fi

    echo $RESULT >> $DIFF

    # compare actual merge and expected merge excluding comments
    diff -wB -I '^#' $F1 $F2 > $DIFF_NC

    if [ -s $DIFF_NC ];then
	RESULT="FAILURE"
    else
	RESULT="SUCCESS"
    fi

    echo $RESULT >> $DIFF_NC

done
popd
