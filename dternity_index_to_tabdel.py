import csv
import os


# ask for an input file
# create an output file that removes the existing extension and adds "_tab.txt" to the end

input_file = input("Enter the file you want to transform: ")
output_file = input_file.rsplit('.', 1)[0] + "_tab.txt"

# open output for writing, add a header line with column names

output_fh = open(output_file, "w", encoding='utf-8-sig')
output_fh.write("file path" + "\t" + "filename"  + "\t" + "file size" + "\t" + "file checksum" + "\t" + "file modified time" + "\n")

# iterate through the input file

with open(input_file, "r", encoding='utf-8-sig', newline='') as file:

    linearray = csv.DictReader(file)

    for la in linearray:

        fs = int(la['size'])


        # create file lists so we can check filenames for comparison

        f_name = la['filename']
        f_path = la['filepath']
        f_size = la['size']
        f_cs = la['hash_code']
        f_bc = la['tape_barcode']


        # output formatted tab delimited
        
        output_fh.write(f_path + "\t" + f_name + "\t" + f_size + "\t" + f_cs + "\t" + "" + "\n")

