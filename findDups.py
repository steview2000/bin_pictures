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

def calcID(path):
	# this functions generates a unique imageID based on the md5sum hash
	f = open(path,'rb')
	id_f = hashlib.md5(f.read()).hexdigest()
	f.close()
	return id_f

PATH = os.path.expanduser('~')+'/Pictures/' # this is the path for the images
DB_file = 'imageDB.json'

fin = open(PATH+DB_file,'r')
dict_list = json.load(fin)
fin.close()

file_list1 = glob.glob(PATH+"**/*.jpg",recursive=True) 
file_list2 = glob.glob(PATH+"**/*.JPG",recursive=True) 
file_list3 = glob.glob(PATH+"**/*.mp4",recursive=True) 
file_list4 = glob.glob(PATH+"**/*.MTS",recursive=True) 
file_list5 = glob.glob(PATH+"**/*.MOV",recursive=True) 
file_list6 = glob.glob(PATH+"**/*.CR2",recursive=True) 
file_list = file_list1 + \
			file_list2 + \
			file_list3 + \
			file_list4 + \
			file_list5 +\
			file_list6

N = len(file_list)
ID_list = []

fout = open('dups.log','w')

for i in range(N):
	print("%d/%d"%(i,N))
	ID = calcID(file_list[i])
	if ID in ID_list:
		fout.write(file_list[i])
		fout.write("\n")
		print(file_list[i])
	ID_list.append(ID)	

fout.close()
