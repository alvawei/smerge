#!/bin/bash

#./run_diff.sh $2/conflicts

# The tested repository
REPO=$1

CONFLICTS=0
MODIFIED=0
UNRESOLVED=0

while read line; do
    if [[ $line =~ (.*)[[:space:]](.*)/(.*) ]]; then
	NUM=${BASH_REMATCH[1]}
	MODIFIED=$((MODIFIED + BASH_REMATCH[2]))
	CONFLICTS=$((CONFLICTS + BASH_REMATCH[3]))
    fi
done < $2/result.txt

UNRESOLVED=$((CONFLICTS - MODIFIED))

# Calculate percentages
P_MODIFIED=$((MODIFIED*100/CONFLICTS))

P_UNRESOLVED=$((UNRESOLVED*100/CONFLICTS))


echo "Repo,Conflicts,Modified,Unresolved,%Modified,%Unresolved" > ${REPO}.csv
printf "%s,%d,%d,%d,%d,%d\n" "$REPO" "$CONFLICTS" "$MODIFIED" "$UNRESOLVED" "$P_MODIFIED" "$P_UNRESOLVED" >> ${REPO}.csv
