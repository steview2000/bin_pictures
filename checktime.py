#!/usr/bin/python3

import subprocess
from subprocess import PIPE
import shutil
import json
import glob
from PIL import Image
import sys
import os
import hashlib
import exifread


PATH = os.path.expanduser('~')+'/Pictures/' # this is the path for the images
DB_file = 'imageDB.json'

fin = open(PATH+DB_file,'r')
dict_list = json.load(fin)
fin.close()

# First look, whether the same path filename exists
for dict_entry in dict_list:
	date = dict_entry['DateTime']
	file_name = dict_entry['File']
	if date != '':
		year_date = date.split(":")[0]
		year_file = file_name.split("/")[4]
		if year_date != year_file:
			print("")
			print(file_name)
			print(year_date)
			print(year_file)


