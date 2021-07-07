# Copyright 2021, University of Notre dname

# this program compares two lists of files
# the input format for file is file path \t filename \t filesize \t checksum \t modified time stamp
# first we need to group directories and files

import csv
import sys
import os
import re

def compare_files (file_groups, directory_list, dirs, dirs2):

	file_matches = 0
	size_matches = 0
	filenames_diff_percent = 0
	filesize_diff_percent = 0

	if dirs in file_groups["one"] and dirs2 in file_groups["two"]:
                for files in file_groups["one"][dirs]:
                        for files2 in file_groups["two"][dirs2]:
                                if files["filename"] == files2["filename"]:
                                        file_matches += 1
                                        if files["size"] == files2["size"]:
                                                size_matches += 1



                if directory_list["one"][dirs]["metadata"]["number_of_files"] != 0:
                        filenames_diff_percent = 100 - ((abs(file_matches - directory_list["one"][dirs]["metadata"]["number_of_files"]) / directory_list["one"][dirs]["metadata"]["number_of_files"]) * 100)


                if directory_list["one"][dirs]["metadata"]["number_of_files"] != 0:
                        filesize_diff_percent = 100 - ((abs(size_matches - directory_list["one"][dirs]["metadata"]["number_of_files"]) / directory_list["one"][dirs]["metadata"]["number_of_files"]) * 100)

	return filenames_diff_percent, filesize_diff_percent, file_matches, size_matches


def compare_directory_lists (directory_list, dirs, dirs2):

		directory_name_match = 0

		for ds in directory_list["one"][dirs]["directories"]:
			for ds2 in directory_list["two"][dirs2]["directories"]:
				if ds == ds2:
					directory_name_match += 1

		return directory_name_match

def remove_substr(string, substr, location):

        new_string = ""

        if location == "start":
                if string.startswith(substr):
                        new_string = string[len(substr):]

        elif location == "end":
                if string.endswith(substr):
                        strlen = len(string)
                        stindex = strlen - len(substr)
                        new_string = string[:stindex]

        return new_string


def config (filename):
        # open configuration file and read in values into a dictionary

        conf = open(filename, "r")
        confcont = conf.read().splitlines()

        configuration = {}
        for item in confcont:
                if '#' not in item and ':' in item:
                        (k, v) = item.split(":", 1)
                        configuration[k] = v

        # validate configuration

        config_required = ["input_one", "input_two", "start_dir_one", "start_dir_two", "match_report", "certainty_offset"]
        error = ""

        for item in config_required:
                if item not in configuration.keys():
                        error += " Error: " + item + " is required and not in configuration.\n"

        return configuration, error


# get configuration options from config.yml

conf, err = config("compare_config.yml")


if err:
        print(err)
        quit()


# certainty adjustment is 100 - whatever the user enters

i = 0

input_files = {"one":conf["input_one"], "two":conf["input_two"]}
start_dirs = {"one":conf["start_dir_one"], "two":conf["start_dir_two"]}
output_file = {"rpt_m":conf["match_report"]}
certainty_adjustment = int(conf["certainty_offset"])


# determine how many directories are

start_dirs_minus_one= {}

for keys in start_dirs:

        dirname = os.path.basename(start_dirs[keys])
        dir_sec = remove_substr(start_dirs[keys], "/", "start").split("/")
        start_dirs_minus_one[keys] = remove_substr(start_dirs[keys], "/" + dirname, "end")



# create dictionary entries for each of the files - essentially "one" and "two"

file_groups = {}

for keys in input_files:

	file_groups.update({keys:{}})

# iterate through both lists of files and combine file metadata so that it is tied to a directory in a complex array that is made up of dictionaries and lists
# the data structure is file_groups[dictionary - one OR two][dictionary - directory_full_path][files][list - 0 ... n files][file_metadata: filename, size, checksum if available, modified time stamp, abbreviated file path]

for key in input_files:

	print("Starting to process data into a list of files for input file " + key)

	with open(input_files[key], encoding='utf-8-sig', newline='') as tsv:
		for line in csv.DictReader(tsv, delimiter="\t"):

			dir_match = 0

			abbrev_file_path = ""

			if start_dirs[key]:
				if line['file path'].startswith(start_dirs[key]):
					abbrev_file_path = line['file path'][len(start_dirs[key]):]
					dir_match = 1


			fp = os.path.dirname(line['file path'])
			dn = os.path.basename(fp)

			afp = abbrev_file_path
			fn = line['filename']
			fs = line['file size']
			fc = line['file checksum']
			fm = line['file modified time']

			temp = {}
			temp = {'filename':fn, 'size':fs, 'checksum':fc, 'modified':fm, 'abfp': afp}

			if dir_match:
				if fp not in file_groups[key].keys():
						file_groups[key][fp] = []
						file_groups[key][fp].append(temp)
				else:
					file_groups[key][fp].append(temp)
	print("Process complete.\n")



# process the lists of files to create a list of directories and directory metadata - paths, names, total # of files, total directory sizes,

directory_list = {}

for keys in file_groups:

	print("Starting to organize file data into a list of directories and directory metadata for input file " + keys)

	directory_list[keys] = {}

	i = 0
	for dirs in file_groups[keys]:
		i += 1
		file_size_total = 0

		# check before initializing the variable set
		if dirs not in directory_list[keys].keys():
			directory_list[keys][dirs] = {"metadata":{}, "directories":[]}

		# create an abbreviated directory string, it is the full path - the path prefixes

		abbrev_dir = ""
		if start_dirs[keys]:
			abbrev_dir = remove_substr(dirs, start_dirs[keys], "start")


        # make sure the parent directory exists, then create a list of subdirectories for each directory
        # first we have to make sure that the program doesn't consider directories above the starting directories
        # and we need to make sure that we add directories only when the parent directory has a legitimate name
        # include the current parent in the directories extrapolated directly from files

		dname = os.path.basename(dirs)
		entry_dname = dname
		parent_path = remove_substr(dirs, "/" + dname, "end")
		entry_parent_path = parent_path
		parent_dname = os.path.basename(parent_path)
		entry_parent_dname = parent_dname

		while parent_path and parent_path != start_dirs_minus_one[keys]:

			parent_abbrev_dir = ""
			if start_dirs[keys]:
				parent_abbrev_dir = remove_substr(parent_path, start_dirs[keys], "start")

			if parent_path not in directory_list[keys].keys():
				grandparent_path = remove_substr(parent_path, "/" + parent_dname, "end")
				grandparent_dname = os.path.basename(grandparent_path)
				directory_list[keys][parent_path] = {"metadata":{'full_path':parent_path, 'abbreviated_path':parent_abbrev_dir,'directory_name':parent_dname, 'parent':grandparent_dname, 'number_of_files':0, 'directory_size':0}, "directories":[]}


			# if "directories" not in directory_list[keys][parent_path].keys():
			# directory_list[keys][parent_path]["directories"] = []

			if dname not in directory_list[keys][parent_path]["directories"]:
				directory_list[keys][parent_path]["directories"].append(dname)

			dname = os.path.basename(parent_path)
			parent_path = remove_substr(parent_path, "/" + dname, "end")
			parent_dname = os.path.basename(parent_path)



		# total files in a directory is calculated based on the number of files in the file_group list for a specific directory

		tot_files = len(file_groups[keys][dirs])

		# this itterates over each of the files in a directory and creates a sum of file sizes to determine the size of the directory in bytes

		for details in file_groups[keys][dirs]:
			file_size_total += int(details["size"])

			# this assigns directory metadata to each directory entry

		directory_list[keys][dirs]["metadata"] = {'full_path':dirs, 'abbreviated_path':abbrev_dir,'directory_name':entry_dname, "parent": entry_parent_dname, 'number_of_files':tot_files, 'directory_size':file_size_total}

	print("Process complete.\n")


# this section of the code opens report files for writing, determines the match criteria, captures which directories matching, and outputs the matches

rpt_m = open(output_file["rpt_m"], "w", encoding='utf-8-sig')
rpt_m.write("Match Status\tDirectory One\tDirectory Two\t# of Files\tSize of Directory (in bytes)\tPercent File Name Matches\tPercent File Size Matches\tDirectory Count\tDirectory Name Matches\n")


dir_exact_matches = 0
dir_candidate_matches = 0
dir_no_match = 0
directory_matches = 0
dir_count = 0
dir2_count = 0
fndp = 0.0
fsdp = 0.0
fm = 0
sm = 0
fp_one = ""
fp_two = ""

i = 0

print("Start directory comparison and report printing.")

match_status = "None"

for dirs in sorted(directory_list["one"].keys()):

	match = 0
	temp_holder = {}

	for dirs2 in directory_list["two"].keys():

		match2 = 0

		# create a dictionary of match indicators and set them based on the presence of the data they related to

		matches = {"dn":0, "nof":0, "ds":0, "ap":0, "nod":0, "nmod":0}

		if directory_list["one"][dirs]["metadata"]["directory_name"] == directory_list["two"][dirs2]["metadata"]["directory_name"]:
			matches["dn"] = 1
		if directory_list["one"][dirs]["metadata"]["number_of_files"] == directory_list["two"][dirs2]["metadata"]["number_of_files"]:
			matches["nof"] = 1
		if directory_list["one"][dirs]["metadata"]["directory_size"] == directory_list["two"][dirs2]["metadata"]["directory_size"]:
			matches["ds"] = 1
		if directory_list["one"][dirs]["metadata"]["abbreviated_path"] == directory_list["two"][dirs2]["metadata"]["abbreviated_path"]:
			matches["ap"] = 1

		# calculate the delta between the primary directories and the secondary directories

		ds_diff_percent = 0;
		if directory_list["two"][dirs2]["metadata"]["directory_size"] != 0:
			ds_diff_percent = 100 - ((abs(directory_list["one"][dirs]["metadata"]["directory_size"] - directory_list["two"][dirs2]["metadata"]["directory_size"]) / directory_list["two"][dirs2]["metadata"]["directory_size"]) * 100)

		fn_diff_percent = 0;
		if directory_list["two"][dirs2]["metadata"]["number_of_files"] != 0:
			fn_diff_percent = 100 - ((abs(directory_list["one"][dirs]["metadata"]["number_of_files"] - directory_list["two"][dirs2]["metadata"]["number_of_files"]) / directory_list["two"][dirs2]["metadata"]["number_of_files"]) * 100)

		fp_one = directory_list["one"][dirs]["metadata"]["full_path"]
		fp_two = directory_list["two"][dirs2]["metadata"]["full_path"]


		# first check for directory name matches

		if matches["dn"]:


			# if the directory name matches, check the directory and file numbers and name matches

			directory_matches = compare_directory_lists(directory_list, dirs, dirs2)
			fndp, fsdp, fm, sm = compare_files(file_groups, directory_list, dirs, dirs2)

			# this section identifies directories that have exactly the same matching number of files and acculative directory size
			# we also need to account for directories that don't have files

			if dirs in directory_list["one"].keys():
				dir_count = len(directory_list["one"][dirs]["directories"])

			if dirs2 in directory_list["two"].keys():
				dir2_count = len(directory_list["two"][dirs2]["directories"])

			if dir_count == dir2_count:
				matches["nod"] = 1

			if dir_count == directory_matches:
				matches["nmod"] = 1

			# this is a placeholder for a directory name match - in this case, the data will be used for a candidate match,
			# but only if there are no other types of matches

			temp_holder = {"fp_one":fp_one, "fp_two":fp_two,"dir_count":dir_count, "dir2_count":dir2_count,"directory_matches":directory_matches,"fm":fm,"sm":sm,"ds":directory_list["two"][dirs2]["metadata"]["directory_size"], "nf":directory_list["two"][dirs2]["metadata"]["number_of_files"]}


			# next, check for a match in number of files in the directory and aggregate size in the directory in bytes and the number of subdirectories

			if matches["nof"] and matches["ds"] and matches["nod"]:

				if directory_list["one"][dirs]["metadata"]["number_of_files"] == 0:

					if matches["nod"] and matches["nmod"] and directory_list["one"][dirs]["metadata"]["parent"] == directory_list["two"][dirs2]["metadata"]["parent"]:
						match = 1
						match2 = 1
						dir_exact_matches += 1
						match_status = "Exact - Directory Only"

				else:
					if directory_list["one"][dirs]["metadata"]["number_of_files"] == fm and directory_list["one"][dirs]["metadata"]["number_of_files"] == sm:
						match = 1
						match2 = 1
						dir_exact_matches += 1
						match_status = "Exact"



			# if number of files and aggregate size do not match, check for matches that are close

			elif fn_diff_percent > (certainty_adjustment) and ds_diff_percent > (certainty_adjustment):

				if fndp  > (certainty_adjustment) and fsdp  > (certainty_adjustment):

					match = 1
					match2 = 1
					dir_candidate_matches += 1
					match_status = "Percentage Candidate"

		if match2:
			rpt_m.write(match_status + "\t" + fp_one + "\t" + fp_two + "\t" + str(round(fn_diff_percent, 3)) + " (" + str(directory_list["one"][dirs]["metadata"]["number_of_files"]) + " / " + str(directory_list["two"][dirs2]["metadata"]["number_of_files"]) + ")" + "\t" + str(round(ds_diff_percent, 3)) + " (" + str(directory_list["one"][dirs]["metadata"]["directory_size"]) + " / " + str(directory_list["two"][dirs2]["metadata"]["directory_size"]) + ")" + "\t" + str(round(fndp, 3)) + " (" + str(directory_list["one"][dirs]["metadata"]["number_of_files"]) + " / " + str(fm) + ")" + "\t" + str(round(fsdp, 3)) + " (" + str(directory_list["one"][dirs]["metadata"]["number_of_files"]) + " / " + str(sm) +")" + "\t" + str(dir_count) + " / " + str(dir2_count) + "\t"   + str(dir_count) + " / "  + str(directory_matches) + "\n")


    # this prints the directory when no match is found

	if not match:


		if temp_holder:
			dir_candidate_matches += 1
			match_status = "Candidate - Directory Name"
		else:
			temp_holder = {"fp_one":fp_one, "fp_two":"","dir_count":"", "dir2_count":"","directory_matches":"","fm":"","sm":"","ds":"", "nf":""}
			fp_two = ""
			dir_no_match += 1
			match_status = "None"

		#rpt_m.write("None\t" + directory_list["one"][dirs]["metadata"]["full_path"] + "\t" + "\t" + "\t" + "\t" + "\t"  + "\t" + str(dir_count) + " / " + str(dir2_count) + "\t" + str(directory_matches)  + " / " + str(dir_count) +   "\n")
		rpt_m.write(match_status + "\t" + fp_one + "\t" + temp_holder["fp_two"] + "\t" + " (" + str(directory_list["one"][dirs]["metadata"]["number_of_files"]) + " / " + str(temp_holder["nf"]) + ")" + "\t" + " (" + str(directory_list["one"][dirs]["metadata"]["directory_size"]) + " / " + str(temp_holder["ds"]) + ")" + "\t" + " (" + str(directory_list["one"][dirs]["metadata"]["number_of_files"]) + " / " + str(temp_holder["fm"]) + ")" + "\t" + " (" + str(directory_list["one"][dirs]["metadata"]["number_of_files"]) + " / " + str(temp_holder["sm"]) +")" + "\t" + str(temp_holder["dir_count"]) + " / " + str(temp_holder["dir2_count"]) + "\t"   + str(temp_holder["dir_count"]) + " / "  + str(temp_holder["directory_matches"]) + "\n")


    # this counter provides some feedback for long comparisons

	i += 1
	if i % 500 == 0:
                print(str(i) + " out of " + str(len(directory_list["one"])) + " directories processed.")

print("Process complete.\n")


# print some statistical feedback

for key in file_groups.keys():
	print("File " + key + " has "  + str(len(directory_list[key])) + " directories.")

print("\nThere were " + str(dir_exact_matches) + " exact matches and " + str(dir_candidate_matches) + " candidates.\n" + "There were " + str(dir_no_match) + " that did not match.")
