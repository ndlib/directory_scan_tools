# Copyright 2021, University of Notre dname

import os
import datetime

# i is a global itterator so we can print out progress
i = 0

def run_fast_scandir(dir, ext, docfile, dirfile, errfile):    # dir: str, ext: list, docfile: filehandle, dirfile: filehandle

    # inc is the incremental number of files after which there is some output printed
    inc = 200
    subfolders, files = [], []
    global i

    # this checks if an entry is a file or a directory and adds it to the correct list
    for f in os.scandir(dir):
        i += 1
        try:
            if i % inc == 0:
                print(str(i) + " processed")
            if f.is_dir():
                dirfile.write(f.path  + "\n")
                subfolders.append(f.path)
            if f.is_file():
                files.append(f.path)
                # 9999 is the last year datetime can process - 11:59pm on Dec 31, 9999 is 253402318740 in unix time
                mdfd = os.path.getmtime(f.path) # str(datetime.datetime.fromtimestamp(os.path.getmtime(f.path)))
                if(mdfd < 253402318740):
                    mdfd_str = str(datetime.datetime.fromtimestamp(mdfd))
                else:
                    mdfd_str = "out of date range: " + str(mdfd)


                if not ext:
                    docfile.write(f.path + "\t" + f.name + "\t" + str(os.path.getsize(f))  + "\t" + "" + "\t" + mdfd_str + "\n")
                    # format should be path, filename, size, checksum, date modified
                else:
                    if os.path.splitext(f.name)[1].lower() in ext:
                        docfile.write(f.path + "\t" + f.name + "\t" + str(os.path.getsize(f))  + "\t" + "" + "\t" + mdfd_str + "\n")
        except Exception as e:
            errfile.write("Item " + str(i) + " " + f.path + " " + str(e) + "\n")

    # this section is to recursively scan folders
    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext, docfile, dirfile, errfile)
        subfolders.extend(sf)
        files.extend(f)

    return subfolders, files

# the program asks the user for a directory, an output file name pre-append for the output files, and if you want to filter by file extesion

folder = input("Enter the full path to the directory you want to scan: ")
fn = input("Enter some letters that will be pre-appended to the output file names: ")
fes = input("Specify any file extensions (inlcude the .) you would like to filter by separated by a space (leave it blank if you don't want to filter): ")


#open an error file
error = open("file_lists/" + fn + "_errors.txt", "w", encoding='utf-8-sig')

# open and write to a files file and a directories file
documents_file = open(fn + "_files.txt", "w", encoding='utf-8-sig')
documents_file.write("file path" + "\t" + "filename"  + "\t" + "file size" + "\t" + "file checksum" + "\t" + "file modified time" + "\n")


directories_file = open(fn + "_directories.txt", "w", encoding='utf-8-sig')
directories_file.write("directory path" + "\n")

print("Starting process ....")

extensions = fes.split()

sf, f = run_fast_scandir(folder, extensions, documents_file, directories_file, error) # ([],[]) # run_fast_scandir(folder, extensions)


documents_file.close()
directories_file.close()


print("Process complete")
