#!/bin/bash

pushd $1
for FILE in `ls *_actual.py`; do
    FILENAME=${FILE::-10}
    F1=${FILENAME}_actual.py
    F2=${FILENAME}_expected.py

    DIFF=${diff $F1 $F2}

    if [ -z DIFF ];then
	RESULT='SUCCESS'
    else
	RESULT='FAILURE'
    fi

    RESULT > ${FILENAME}.out
done
popd
