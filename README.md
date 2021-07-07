# directory_scan_tools

## compare_file_lists.py

### Purpose
compare_file_lists.py takes two standardized tab delimited file of file information

file path | filename | file size | file checksum | file modified time

file checksum and file modified time can be blank and are not currently used for comparisons

It then groups the list of files into a list of directories and metadata:
  1. Name of Directory
  2. Number of Files in the Directory
  3. Total Size of all Files in the Directory (in bytes)

The program then compares this metadata to each other to determine if a directory is likely the same in both filespaces.
It compares the metadata listed above, but also compares the names of the files in the directory along with the individual file sizes.

The program also calculates the number of directories in a directory, as well as comparing directory names.  Because the program does this from a list of files, the data is not complete.  If a filespace has no files in it, it may not be picked up by the program.

### Algorithm
To determine whether a directory is a match to another directory, the program uses file and directory metadata.

  1. First, it checks to see the directory names match
  2. Second, it checks to see if the number of files, the aggregate size of the directory, and the number of internal directories match
    2a. The progam checks to see if there are any files in the directory, if not, it is considered "Exact - Directory Only"
    2b. If there are files in the directory, the program checks each individual file size and file name, embedded directories by number and name, if these all match it is considered "Exact"
  3. If the above are not matches, the program looks at file name and file size matches that are within a percentage margin of error and marks these as "Percentage Candidates"
  4. Directories that only match by name are marked as "Candidate - Directory Name" and only if there wasn't an exact or candidate match
  5. The rest are labled as "None" for no match

**Note: The comparison is one direction.  The program checks for matches to input file one.  If you want to check the other direction, simply switch the file paths.**

### Configuration
The configuration file is called compare_config.yml and is in basic yaml syntax
```
name:value
```

First, enter the path to the file you want to compare and the file you want to compare it to.  Paths can be absolute OR relative to the script.

```
input_one:some/file/path.txt
input_two:some/file/path.txt
```
Next, choose how far up the directory structure you want to go.  You may wish to start in the middle of a file structure because two different file spaces may have different structure.  All preceding directories to these paths will be ignored.

```
start_dir_one:/a/starting/directory
start_dir_two:/a/starting/directory
```

Next, you can specify the name of your output report.

```
match_report:match_report.txt
```

And then finally, you can set a matching offset, if file sizes, file names, directory sizes, and number of files are within a percentage of error, they will be listed as candidates.  In this case, we have set this at 96%.

```
certainty_offset:96
```

### Usage
