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

## Example
```
// Common ancestor:
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
// Yours:
public static ArrayList doSomething(length) {
  ArrayList arr = new ArrayList();
  for (int i = 0; i < length; i++) {
    arr.add(i);
  }

  return arr;
}

Note the white space on different line:
```
// Theirs
public static ArrayList doSomething(length) {
  ArrayList arr = new ArrayList();
  
  for (int i = 0; i < length; i++) {
    arr.add(i);
  }
  return arr;
}
```

Conflict resolution after using Smerge
```
// Final
public static ArrayList doSomething(length) {
  ArrayList arr = new ArrayList();
  
  for (int i = 0; i < length; i++) {
    arr.add(i);
  }
  
  return arr;
}
```
