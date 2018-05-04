# smerge
## Status
We use Travis CI for continuous integration (click the badge below). 
[![Build Status](https://travis-ci.org/alvawei/smerge.svg?branch=master)](https://travis-ci.org/alvawei/smerge)

## Build
*smerge* uses gradle for project dependencies. The build system can be invoked through the following command:

```
./gradlew assemble
```

# User Manual
Smerge is a merge tool that resolves merge conflicts with abstract syntax trees (ASTs) (see below for details). By parsing the source code into ASTs, Smerge is able to automatically resolve false conflicts (conflicts where the differences are purely cosmetic; e.g. variable names or whitespace), as well as provide an intuitive tree-based candidate resolution for conflicts with structural differences in the source code. This in turn allows developers to spend less time fixing trivial merge conflicts as Smerge will resolve them automatically.


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

Note that if no file is given, the mergetool will be ran on every conflicting file. Currently, smerge can be applied to conflicting python files. We plan to add more languages in the future.

## Example

Here is a simple example of how Smerge can be applied to handle a trivial merge conflict
```
1  # Common ancestor (Base):
2  x = 0
3  def doSomething(modify)
4    self.x = 2;
5  
```

Note the change in x assignment on line 4 below.
```
1  # Yours (Local):
2  x = 0
3  def doSomething(modify)
4    self.x = 3
5  
```

Note the other user's addition of an if statement spanning from lines 4-5.
```
1  # Theirs (Remote)
2  x = 0
3  def doSomething(modify)
4    if modify
5        self.x = 2;
6    
```

Conflict resolution after using Smerge:
```
1  # Final (AST Merged)
2  x = 0
3  def doSomething(modify)
4    if modify
5        self.x = 3;
6    
```
Git's standard merge tool will flag a conflict like this as unmergable. After running Smerge, the tool catches this and captures the intent of both programmers. This is seen in line 4 of the conflict resolution as the local `this.x = 3` statement is captured as well as the remote `if` condition.


## Abstract Syntax Tree Merging
Once Smerge generates the ASTs, it checks where the conflict is located in the tree. If the trees are identical, then the differences are cosmetic and the conflict is a false conflict. False conflicts are resolved by choosing the changes from the newer branch. If the differences are in separate subtrees, the conflict can be resolved by performing a tree merge on the ASTs.

If the differences occur in the same subtree, then the conflict involves overlapping structural differences. In this case, Smerge uses several heuristics to produce a candidate merge, but the final resolution is left up to the developer.
