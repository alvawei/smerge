#!/bin/bash

./run_diff.sh $2

# The tested repository
REPO=$1

# Number of conflicts smerge failed to merge
UNRESOLVED=$(grep FAILURE $2/result.txt | wc -l)

# Number of conflicts smerge merged
RESOLVED=$(grep SUCCESS $2/result.txt | wc -l)

# Number of Smerge merges identical to human merges
PERFECT=$(grep SUCCESS $2/*.out | wc -l)

# Number of Smerge merges identical to human merges, ignoring comments
ALL_PERFECT_NC=$(grep SUCCESS $2/*_nc.out | wc -l)

# Total number of tested conflicts
CONFLICTS=$((RESOLVED+UNRESOLVED))

# Number of Smerge merges identical to human merges but differing in comments
PERFECT_NC=$((ALL_PERFECT_NC-PERFECT))

# Number of incorrect merges
INCORRECT=$((RESOLVED-ALL_PERFECT_NC))

# Calculate percentages
P_CORRECT=$((PERFECT*100/CONFLICTS))

P_CORRECTNC=$((PERFECT_NC*100/CONFLICTS))

P_UNRESOLVED=$((UNRESOLVED*100/CONFLICTS))

P_INCORRECT=$((INCORRECT*100/CONFLICTS))


# echo "Repo,Conflicts,Unresolved,Correct,CorrectNC,Incorrect,%Correct,%CorrectCW,%Unresolved,%Incorrect" > ${REPO}.csv
printf "%s,%d,%d,%d,%d,%d,%d,%d,%d,%d\n" "$REPO" "$CONFLICTS" "$UNRESOLVED" "$PERFECT" "$PERFECT_NC" "$INCORRECT" "$P_CORRECT" "$P_CORRECTNC" "$P_UNRESOLVED" "$P_INCORRECT" > ${REPO}.csv
