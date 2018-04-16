# User Manual
## Installation
* Clone the Smerge repository to ~/.
```bash
    [mergetool "conflerge-tree"]
                cmd = java -jar ~/Conflerge/ConflergeTree.jar \$BASE \$LOCAL \$REMOTE \$MERGED
    [mergetool "conflerge-token"]
        cmd = java -jar ~/Conflerge/ConflergeToken.jar \$BASE \$LOCAL \$REMOTE \$MERGED
    [merge]
        tool = conflerge-tree
        tool = conflerge-token
```

## Usage
`git mergetool --tool=smerge <conflicting file>`

## Options

## GUI Usage
