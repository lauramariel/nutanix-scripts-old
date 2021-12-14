# scripts

# calm_import_bp.py

## Notes

When importing from a directory, subfolders are not traversed.

## Usage

```
usage: calm_bp_import.py [-h] (-d D | -f F) -j J -p P -u U

Script to import Calm blueprints automatically from a directory, or a single
file

optional arguments:
  -h, --help  show this help message and exit
  -d D        Directory to read from, required if -f is not present.
  -f F        File to import, required if -d is not present. Full file path
              required.
  -j J        Project to import to
  -p P        Prism Central IP
  -u U        Prism User
```

## Examples

### Importing multiple files that are located in a directory folder

```
$ python3 calm_bp_import.py -d ~/blueprints -j default -p 34.83.7.88 -u admin
Password:
======== Not processing bp (Doesn't appear to be a JSON file) ========

======== Not processing .DS_Store (Doesn't appear to be a JSON file) ========

======== Processing NewApp.json ========
BP name will be: NewApp
Path to file: /Users/laura.jordana/blueprints/NewApp.json
Processing file /Users/laura.jordana/blueprints/NewApp.json
Blueprint NewApp imported successfully

======== Processing MyCustomApp.json ========
BP name will be: MyCustomApp
Path to file: /Users/laura.jordana/blueprints/MyCustomApp.json
Processing file /Users/laura.jordana/blueprints/MyCustomApp.json
Blueprint MyCustomApp imported successfully

======== Processing MyApp.json ========
BP name will be: MyApp
Path to file: /Users/laura.jordana/blueprints/MyApp.json
Processing file /Users/laura.jordana/blueprints/MyApp.json
Blueprint MyApp imported successfully

3 files processed
2 files not processed
```

### Importing a single file

```
$ python3 calm_bp_import.py -f ~/blueprints/bp/TestApp.json -j default -p 34.83.7.88 -u admin
Password:
Only processing one file.
/Users/laura.jordana/blueprints/bp/TestApp.json
Processing file /Users/laura.jordana/blueprints/bp/TestApp.json
Blueprint TestApp imported successfully
```