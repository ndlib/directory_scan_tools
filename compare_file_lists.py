# this program compares two lists of files
# the input format for file is file path \t filename \t filesize \t checksum \t modified time stamp
# first we need to group directories and files

import csv
import sys
import os

def compare_files (file_groups, directory_list, dirs, dirs2):

	file_matches = 0
	size_matches = 0

	for files in file_groups["one"][dirs]:
		for files2 in file_groups["two"][dirs2]:
			if files["filename"] == files2["filename"]:
				file_matches += 1
				if files["size"] == files2["size"]:
					size_matches += 1


	filenames_diff_percent = 0
	if directory_list["one"][dirs]["number_of_files"] != 0:
		filenames_diff_percent = 100 - ((abs(file_matches - directory_list["one"][dirs]["number_of_files"]) / directory_list["one"][dirs]["number_of_files"]) * 100)

	filesize_diff_percent = 0
	if directory_list["one"][dirs]["number_of_files"] != 0:
		filesize_diff_percent = 100 - ((abs(size_matches - directory_list["one"][dirs]["number_of_files"]) / directory_list["one"][dirs]["number_of_files"]) * 100)

	return filenames_diff_percent, filesize_diff_percent, file_matches, size_matches


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

        config_required = ["input_one", "input_two", "start_dir_one", "start_dir_two", "match_report", "candidate_report", "certainty_offset"]
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




i = 0

input_files = {"one":conf["input_one"], "two":conf["input_two"]}
start_dirs = {"one":conf["start_dir_one"], "two":conf["start_dir_two"]}
output_file = {"rpt_m":conf["match_report"], "rpt_c":conf["candidate_report"]}
certainty_adjustment = int(conf["certainty_offset"])

# create dictionary entries for each of the files - essentially "one" and "two"

file_groups = {}

for keys in input_files:
	file_groups.update({keys:{}})

# iterate through both lists of files and combine file metadata so that it is tied to a directory in a complex array that is made up of dictionaries and lists
# the data structure is file_groups[dictionary - one OR two][dictionary - directory_full_path][list - 0 ... n files][file_metadata: filename, size, checksum if available, modified time stamp, abbreviated file path]

for key in input_files:
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


# process the lists of files to create a list of directories and directory metadata - paths, names, total # of files, total directory sizes, 

directory_list = {}

for keys in file_groups:

	directory_list[keys] = {}

	i = 0
	for dirs in file_groups[keys]:
		i += 1
		file_size_total = 0

		# create an abbreviated directory string, it is the full path - the path prefixes

		abbrev_dir = ""
		if start_dirs[keys]:
			if dirs.startswith(start_dirs[keys]):
				abbrev_dir = dirs[len(start_dirs[keys]):]

		# total files in a directory is calculated based on the number of files in the file_group list for a specific directory

		tot_files = len(file_groups[keys][dirs])

		# this itterates over each of the files in a directory and creates a sum of file sizes to determine the size of the directory in bytes

		for details in file_groups[keys][dirs]:
			file_size_total += int(details["size"])

		# this assigns directory metadata to each directory entry

		directory_list[keys][dirs] = {'full_path':dirs, 'abbreviated_path':abbrev_dir,'directory_name':os.path.basename(dirs), 'number_of_files':tot_files, 'directory_size':file_size_total}


# this section of the code opens report files for writing, determines the match criteria, captures which directories match, and outputs the matches

rpt_m = open(output_file["rpt_m"], "w", encoding='utf-8-sig')
rpt_m.write("Match Status\tDirectory One\tDirectory Two\t# of Files\tSize of Directory (in bytes)\tPercent File Name Matches\tPercent File Size Matches\n")

rpt_c = open(output_file["rpt_c"], "w", encoding='utf-8-sig')
rpt_c.write("Match Status\tDirectory One\tDirectory Two\t# of Files\tSize of Directory (in bytes)\tPercent File Name Matches\tPercent File Size Matches\n")

dir_exact_matches = 0
dir_candidate_matches = 0

i = 0

for dirs in sorted(directory_list["one"].keys()):
	for dirs2 in directory_list["two"].keys():

		# create a dictionary of match indicators and set them based on the presence of the data they related to

		matches = {"dn":0, "nof":0, "ds":0, "ap":0}

		if directory_list["one"][dirs]["directory_name"] == directory_list["two"][dirs2]["directory_name"]:
			matches["dn"] = 1
		if directory_list["one"][dirs]["number_of_files"] == directory_list["two"][dirs2]["number_of_files"]:
			matches["nof"] = 1
		if directory_list["one"][dirs]["directory_size"] == directory_list["two"][dirs2]["directory_size"]:
			matches["ds"] = 1
		if directory_list["one"][dirs]["abbreviated_path"] == directory_list["two"][dirs2]["abbreviated_path"]:
			matches["ap"] = 1

		# calculate the delta between the primary directories and the secondary directories

		ds_diff_percent = 0;
		if directory_list["two"][dirs2]["directory_size"] != 0:
			ds_diff_percent = 100 - ((abs(directory_list["one"][dirs]["directory_size"] - directory_list["two"][dirs2]["directory_size"]) / directory_list["two"][dirs2]["directory_size"]) * 100)

		fn_diff_percent = 0;
		if directory_list["two"][dirs2]["number_of_files"] != 0:
			fn_diff_percent = 100 - ((abs(directory_list["one"][dirs]["number_of_files"] - directory_list["two"][dirs2]["number_of_files"]) / directory_list["two"][dirs2]["number_of_files"]) * 100)


		# this section identifies directories that have exactly the same matching number of files and acculative directory size

		if matches["dn"] and matches["nof"] and matches["ds"]:

			dir_exact_matches += 1
			fndp, fsdp, fm, sm = compare_files (file_groups, directory_list, dirs, dirs2)
			rpt_m.write("Exact Match\t" + directory_list["one"][dirs]["full_path"] + "\t" + directory_list["two"][dirs2]["full_path"] + "\t" + str(round(fn_diff_percent, 3)) + " (" + str(directory_list["one"][dirs]["number_of_files"]) + " / " + str(directory_list["two"][dirs2]["number_of_files"]) + ")" + "\t" + str(round(ds_diff_percent, 3)) + " (" + str(directory_list["one"][dirs]["directory_size"]) + " / " + str(directory_list["two"][dirs2]["directory_size"]) + ")" + "\t" + str(round(fndp, 3)) + " (" + str(directory_list["one"][dirs]["number_of_files"]) + " / " + str(fm) + ")" + "\t" + str(round(fsdp, 3)) + " (" + str(directory_list["one"][dirs]["number_of_files"]) + " / " + str(sm) +")" + "\n")

		# this section identifies directories that look very close to matches, but aren't - e.g. they have a random match or they were moved and altered

		elif matches["dn"] and fn_diff_percent > (100-certainty_adjustment) and ds_diff_percent > (100 - certainty_adjustment):

			dir_candidate_matches += 1
			fndp, fsdp, fm, sm = compare_files (file_groups, directory_list, dirs, dirs2)
			rpt_c.write("Candidate Match\t" + directory_list["one"][dirs]["full_path"] + "\t" + directory_list["two"][dirs2]["full_path"] + "\t" + str(round(fn_diff_percent, 3)) + " (" + str(directory_list["one"][dirs]["number_of_files"]) + " / " + str(directory_list["two"][dirs2]["number_of_files"]) + ")" + "\t" + str(round(ds_diff_percent, 3)) + " (" + str(directory_list["one"][dirs]["directory_size"]) + " / " + str(directory_list["two"][dirs2]["directory_size"]) + ")" + "\t" + str(round(fndp, 3)) + " (" + str(directory_list["one"][dirs]["number_of_files"]) + " / " + str(fm) + ")" + "\t" + str(round(fsdp, 3)) + " (" + str(directory_list["one"][dirs]["number_of_files"]) + " / " + str(sm) +")" + "\n")


# print some statistical feedback

for key in file_groups.keys():
	print("File " + key + " has "  + str(len(directory_list[key])) + " directories.")

print("\nThere were " + str(dir_exact_matches) + " exact matches and " + str(dir_candidate_matches) + " candidates.")
			

				
