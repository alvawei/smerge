[![Build Status](https://travis-ci.org/alvawei/smerge.svg?branch=master)](https://travis-ci.org/alvawei/smerge)

# User Manual
Smerge is a merge tool that resolves merge conflicts with abstract syntax trees (ASTs). By parsing the source code into ASTs, Smerge is able to automatically resolve false conflicts (conflicts where the differences are purely cosmetic; e.g. variable names or whitespace), as well as provide an intuitive tree-based candidate resolution for conflicts with structural differences in the source code.

## Abstract Syntax Tree Merging
Once Smerge generates the ASTs, it checks where the conflict is located in the tree. If the trees are identical, then the differences are cosmetic and the conflict is a false conflict. False conflicts are resolved by choosing the changes from the newer branch. If the differences are in separate subtrees, the conflict can be resolved by performing a tree merge on the ASTs.

If the differences occur in the same subtree, then the conflict involves overlapping structural differences. In this case, Smerge uses several heuristics to produce a candidate merge, but the final resolution is left up to the developer.

## Installation
* Clone the *smerge* repository to ~/.
* Update your `.gitconfig` to include: 
```bash
[mergetool "smerge"]
        cmd = java -jar ~/smerge/Merger.jar \"$BASE\" \"$LOCAL\" \"$REMOTE\" \"$MERGED\"
[merge]
        tool = smerge
```
Files to provide are described as follows:

* $BASE: The original file modified into two conflicting versions, $LOCAL and $REMOTE
* $LOCAL: The conflicting file version the user has modified.
* $REMOTE: The conflicting file version of the branch the user is attempting to merge with.
* $MERGED: The output destination where the final merge is written.


## Usage
You may run *smerge* as a [git mergetool](https://git-scm.com/docs/git-mergetool) through the following command:

`git mergetool --tool=smerge <conflicting file>`

Note that if no file is given, the mergetool will be ran on every conflicting file.

## Example

Here is a simple example of how Smerge can be applied to handle a trivial merge conflict
```
1  // Common ancestor (Base):
2  public static void doSomething(boolean modify) {
3    this.x = 2;
4  }
```

Note the white space:
```
1  // Yours (Local):
2  public static void doSomething(boolean modify) {
3    this.x = 3;
4  }
```

Note the white space on different line:
```
1  // Theirs (Remote)
2  public static void doSomething(boolean modify) {
3    if (modify) {
4        this.x = 2;
5    }
6  }
```

Conflict resolution after using Smerge:
```
1  // Final (AST Merged)
2  public static ArrayList doSomething(length) {
3    if (modify) {
4          this.x = 3;
5    }
6  }
```
Git's standard merge tool will flag a conflict like this as unmergable. After running Smerge, the tool catches this and captures the intent of both programmers. This is seen in line 4 of the conflict resolution as the local `this.x = 3` statement is captured as well as the remote `if` condition.
