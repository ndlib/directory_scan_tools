# directory_scan_tools

## compare_file_lists.py

### Purpose
compare_file_lists.py takes two standardized tab delimited file of file information

file path | filename | file size | file checksum | file modified time

file checksum and file modified time can be blank and are not currently used for comparisons

It then groups the list of files into a set of directories that have the following metadata:
1. Name of Directory
2. Number of Files in the Directory
3. Total Size of all Files in the Directory (in bytes)
4. 

### Algorithm
To determine whether a directory is a match to another directory

### Configuration
The configuration file is called compare_config.yml and is in basic yaml syntax
> name:value


### Usage
