# directory_scan_tools

## compare_file_lists.py

### Purpose
compare_file_lists.py takes two standardized tab delimited file of file information

The input files must contain the following:

> file path | filename | file size | file checksum | file modified time

_Note: file checksum and file modified time can be blank and are not currently used for comparisons._

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
The configuration file is called compare_config.yml and is in basic yaml syntax:

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

Usage is simple.  The program has no external dependencies, however you must be running Python 3.8 or above.

Make sure your compare_config.yml is completed and in the same directory as the compare_file_lists.py

> $ python compare_file_lists.py

## directory_contents.py

### Purpose

This program prompts you for a directory path to scan, scans that directory for files, and places them in a tab delimited list formatted specifically for compare_directory_lists.py

The format is:

> file path | filename | file size | file checksum | file modified time

### Usage

This program also has no external dependencies, but requires Python 3.8 or above.

> $ python directory_contents.py

> Enter the full path to the directory you want to scan: /some/directory/path
> Enter some letters that will be pre-appended to the output file names: abc _this will be pre-appended to a string _files.txt_
> Specify any file extensions (include the .) you would like to filter by separated by a space (leave it blank if you don't want to filter): .jpg .html .mov

This will produce a well-formatted tab delimited file with the name abc_files.txt

## dternity_index_to_tabdel.py

### Purpose

This program takes an input file created by the dternity file gateway software and creates a file that is formatted for compare_file_lists.py

## Usage

This program also has no external dependencies, but requires Python 3.8 or above.

> $ python dternity_index_to_tabdel.py

> Enter the file you want to transform: /some/file/on/your/system.txt

The program will create an output file called system_tab.txt
