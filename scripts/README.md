# Evaluation of Smerge

## Reproducing Results
* Follow installation instructions included in the User Manual (README.md) in ~/smerge
* Build *smerge* by running `./gradlew build`
* Make sure all .sh files in `smerge/scripts` have run permission by running `chmod +x *.sh`
* Within the `smerge/scripts` directory, run:
`./test.sh`
* `test.sh` operates by default on the repositories given in `repos.txt`. It first looks at the historical data of the
current repository. From the data, it finds the conflicts and attempts to merge each conflict using our tool. From here,
it compares the output file of our tool with the manual merge that the repository's developers performed. 
* Results are included in `table.csv`. Individual repo results are included in `[repo_name].csv`. 

For reference, the categories on the table are defined below:
* **Conflicts:** The number of merge conflicts (found in conflicting files, not commits) found in the repository’s history with exactly two parents. Here, we define a conflict as a portion of the two parent files that conflict. This means that files can contain multiple conflicts, and If multiple conflicts are found between the two parents, all of those conflicts are counted. This does not include conflicts that result from adding or deleting files in the repository.
* **Modified:** The conflicts that Smerge modified because it deemed the conflict as trivial enough to automatically merge. 
* **Unresolved:** The conflicts that Smerge aborted because it deemed attempting to merge would result in possibly undesired behavior. These conflicts would require manual resolution. 

## References
This evaluation technique is inspired by a predecessor tool: Conflerge.

[1]Hanawalt, G., Harrison, J., & Saksena, I. (2017, March 10). Conflerge: Automatically Resolving Merge Conflicts[Scholarly project]. Retrieved April 5, 2018, from https://github.com/ishansaksena/Conflerge
