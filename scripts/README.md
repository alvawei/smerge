# Evaluation

## Reproducing the results
* Follow the installation guide in the user manual to install smerge
* Ensure that all bash script files in smerge/scripts have execution permission by running:
```
chmod +x *.sh
```
* From smerge/scripts, run:
```
./test.sh
```
* This will run evaluation script on the set of GitHub repositories defined in repos.txt
* Evaluation results on each repository are stored in respective <reponame>.csv