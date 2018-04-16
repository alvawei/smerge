# User Manual
Smerge is a tool used for automating and minimizing user input in merge conflict resolutions.
## Installation
* Clone the Smerge repository to ~/.
* Update your `.gitconfig` to include: 
```bash
    [mergetool "smerge"]
                cmd = java -jar ~/smerge/Merger.jar \$BASE \$LOCAL \$REMOTE \$MERGED
    [merge]
        tool = smerge
```

## Usage
`git mergetool --tool=smerge <conflicting file>`

## Options

## GUI Usage
