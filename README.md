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

## Usage
You may run *smerge* as a [git mergetool](https://git-scm.com/docs/git-mergetool) through the following command:

`git mergetool --tool=smerge <conflicting file>`

Note that if no file is given, the mergetool will be ran on every conflicting file.

## Example
```
// Common ancestor (Base):
public static ArrayList doSomething(length) {
  ArrayList arr = new ArrayList();
  for (int i = 0; i < length; i++) {
    arr.add(i);
  }
  return arr;
}
```

Note the white space:
```
// Yours (Local):
public static ArrayList doSomething(length) {
  ArrayList arr = new ArrayList();
  for (int i = 0; i < length; i++) {
    arr.add(i);
  }

  return arr;
}
```

Note the white space on different line:
```
// Theirs (Remote)
public static ArrayList doSomething(length) {
  ArrayList arr = new ArrayList();
  
  for (int i = 0; i < length; i++) {
  
  for (int i = 0; i < length; i++) {
    arr.add(i);
  }
  return arr;
}
```

Conflict resolution after using Smerge:
```
// Final (AST Merged)
public static ArrayList doSomething(length) {
  ArrayList arr = new ArrayList();
  
  for (int i = 0; i < length; i++) {
    arr.add(i);
  }
  
  return arr;
}
