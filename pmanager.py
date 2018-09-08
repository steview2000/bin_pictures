#!/usr/bin/python3
# TODO filter function
# File via pipe also for tagging

import argparse
import subprocess
from subprocess import PIPE
import shutil
import json
import glob
from PIL import Image
import sys
import os
import hashlib

PATH = os.path.expanduser('~')+'/Pictures/' # this is the path for the images

# Database file
DB_file = 'imageDB.json'

# possible tags
tag_list = ['DateTime','ID','People','Place','Event','tag']

# Video suffix
video_suffix = ['mp4','MP4','mov','MOV','MTS','mpg','MPG']

def get_date_taken(path):
	#print(path)
	# first try the pure python way
	if path[-3:] == 'MPG':
		path = path[:-3]+'THM'
	elif path[-7:] == 'CR2.jpg':
		path = path[:-4]

	p=subprocess.Popen(['exiftool',path],stdin=PIPE,stdout=PIPE,bufsize=1)		
	date1=str(p.communicate()[0],'utf-8')
	exif_list=date1.split("\n")
	dateCreate=''
	for line in exif_list:
		entry = line.split(": ")
		tagname = entry[0].replace(" ","")
		#print(tagname)
		if (tagname == "ContentCreateDate") or \
		(tagname == "Date/TimeOriginal") or \
		(tagname == "CreateDate") or \
		(tagname =="MediaCreateDate"):
			dateCreate = entry[1]
			break

	if dateCreate=='':
		if 'WP_20' in path:
			k = path.find('WP_20')
			year = path[k+3:k+7]
			month = path[k+7:k+9]
			day = path[k+9:k+11]
			hour = path[k+12:k+14]
			minut = path[k+15:k+17]
			dateCreate=(year+':'+month+':'+day+' '+hour+':'+minut)

		elif path[-11] == '_' and path[-23:-19] == 'IMG_':
			k=-22
			year = path[k+3:k+7]
			month = path[k+7:k+9]
			day = path[k+9:k+11]
			hour = path[k+12:k+14]
			minut = path[k+14:k+16]
			sec = path[k+16:k+18]
			dateCreate=(year+':'+month+':'+day+' '+hour+':'+minut+':'+sec)

		elif path[-7] == '.' and path[-10] == '.' and path[-13]=='_':
			k=-23
			year = path[k:k+4]
			month = path[k+5:k+7]
			day = path[k+8:k+10]
			hour = path[k+11:k+13]
			minut = path[k+14:k+16]
			sec = path[k+17:k+19]	
			dateCreate=(year+':'+month+':'+day+' '+hour+':'+minut+':'+sec)
			
	return dateCreate

def get_file_list(arg_list):
	# This function takes care for the file list input. File lists can be given to pmanager
	# either by arguments, or via STDIN (e.g. via a pipe from another program)
	
	# use stdin if it's full                                                        
	if not sys.stdin.isatty():
		print("not")
		input_stream = sys.stdin
		file_list=[]
		for line in input_stream:
			file_list.append(line[:-1])
	# otherwise, read the given filename                                  
	else:
		file_list = arg_list[2:]
	
	if len(file_list)<1:
		print("")
		print("No image file provided!")
		print("List of image files with full path needs to be provided")
		print("either as arguments, or via stdin!!\n")
	return file_list

def calcID(path):
	# this functions generates a unique imageID based on the md5sum hash
	f = open(path,'rb')
	id_f = hashlib.md5(f.read()).hexdigest()
	f.close()
	return id_f

def showImage(filename):
	if filename[-3:] in video_suffix:
		cmd=['mpv','--loopp=inf',filename]
	else:
		cmd=['sxiv',filename]
	subprocess.run(cmd )
	#subprocess.run(['feh','-.','-b','black','--draw-exif','--draw-tinted',filename] )
	#pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,preexec_fn=os.setsid)

################################### For Updating ###################################################
# This file searches for images in the ~/Pictures folder and creates an database that will be saved
# in a json file
def updateDB():
	# just have been moved
	# search for all image files (raw files are ignored
	
	print("Updating the database ......")

	file_list1 = glob.glob(PATH+"**/*.jpg",recursive=True) 
	file_list2 = glob.glob(PATH+"**/*.JPG",recursive=True) 
	file_list3 = glob.glob(PATH+"**/*.jpeg",recursive=True) 
	file_list4 = glob.glob(PATH+"**/*.png",recursive=True) 
	file_list5 = glob.glob(PATH+"**/*.mp4",recursive=True) 
	file_list6 = glob.glob(PATH+"**/*.MTS",recursive=True) 
	file_list7 = glob.glob(PATH+"**/*.MOV",recursive=True) 
	file_list8 = glob.glob(PATH+"**/*.CR2",recursive=True) 
	file_list9 = glob.glob(PATH+"**/*.MPG",recursive=True) 
	file_list = file_list1 + file_list2 + file_list3 + file_list4 + file_list5 + file_list6 +\
				file_list7 + file_list8 + file_list9

	# check whether database already exists. If not create a dictionary that will later
	# be saved in a json database 
	try:
		fin = open(PATH+DB_file,'r')
		dict_list = json.load(fin)
		fin.close()
	except FileNotFoundError:
		dict_list = []

	place_list  = []
	people_list = []
	event_list  = []
	tag_list    = []

	N      = len(dict_list)
	N_file = len(file_list)
	
	print("%d files found!"%N_file)
	print("%d files already in the database!"%N)
	
	# Let's go through all images found and see, whether they have already entries
	change_number = 1
	file_count=0
	for filename in file_list:
		file_count +=1
		
		if filename.find(" ")>-1:
			print("Whitespaces found in: ")
			print(filename)
			print("")
		
		if file_count%200==0:	
			print(("completed: %i/%i")%(file_count,N_file),end='\r')
		
		exist_already = 0

		# First look, whether the same path filename exists
		for dict_entry in dict_list:
			if dict_entry['File'] == filename:
				exist_already = 1
				if dict_entry['ID'] == '':
					dict_entry['ID'] = calcID(filename)
					change_number +=1
				if dict_entry['DateTime'] == "":
					dict_entry['DateTime'] = get_date_taken(filename)

		# If the same path filename was not found, check for the unique ID
		if exist_already ==0:
			f_ID = calcID(filename)
			for dict_entry in dict_list:
				if dict_entry['ID'] == f_ID:
					print('File \"'+dict_entry['File']+'\" has been moved!')
					print(dict_entry['File']+' --> '+filename)
					print('')
					print(("completed: %i/%i")%(file_count,N_file))
					dict_entry['File']=filename
					if exist_already==0:
						exist_already =1
		
		# If also no ID was found, create a new entry
		if exist_already == 0:
			print("New: "+filename)
			change_number +=1
			dict_entry = {'DateTime':'','ID':calcID(filename),'File':filename,'Description':'','People':[],'Place':[],'Event':'','tag':[]}
			try:
				dict_entry['DateTime'] = get_date_taken(filename)		
			except:
				#print(filename)
				print("No DateEntry")
			jout = json.dumps(dict_entry,sort_keys=True,indent=2)
			dict_list.append(dict_entry)

			if filename[-3:] in video_suffix:
				print("Video found!!\n")
				print("Create Thumbnail")
				print(filename)
				retcode = subprocess.call(['ffmpeg','-i',filename,'-frames','1',filename+'_1.jpg'])	
				retcode = subprocess.call(['convert',filename+'_1.jpg',PATH+'play.png.overlay','-gravity','center','-composite',filename+'.THM'])	
				retcode = subprocess.call(['rm',filename+'_1.jpg'])	

	
		if change_number%50 == 0:
			fout = open(PATH+DB_file,'w')
			json.dump(dict_list,fout,sort_keys=True,indent=2)
			fout.close()
		

	# Lets go through the database and see, whether the image still exists
	# If not delete the corresponding entry
	N = len(dict_list)
	toDelete    = []
	miss_Place  = 0
	miss_People = 0
	miss_Date   = 0

	for i in range(N):
		dict_entry = dict_list[i]
		file_to_check = dict_entry['File']	
		if not(file_to_check in file_list):	
			print("Not existing anymore: ")
			print(file_to_check)
			toDelete.append(i)
		elif dict_entry in dict_list[i+1:]:
			print("Duplicated Entry:")
			print(file_to_check)
			toDelete.append(i)
		if len(dict_entry['Place'])<1:
			miss_Place += 1
		if len(dict_entry['People'])<1:
			miss_People += 1
		if len(dict_entry['DateTime'])<1:
			miss_Date += 1

	N=len(toDelete)
	for i in range(N):
		del dict_list[toDelete[N-i-1]]
	
	
	N = len(dict_list)
	
	fout = open(PATH+DB_file,'w')
	json.dump(dict_list,fout,sort_keys=True,indent=2)
	fout.close()
	print('.... done!')

	
	print('\n Entries without Place-tag: %d'%miss_Place)
	print('\n Entries without People-tag: %d'%miss_People)
	print('\n Entries without Date-tag: %d'%miss_Date)

def searchPicOld(arg_list):
	# arg_list is a list of tags that all need to be fullfilled. 
	# the arg_list can have multiple entries like the name of people or of places
	# multiple entries will be connected with a logical AND
	# analyse the arg_list
	
	# Load the josn database with the images
	fin = open(PATH+DB_file,'r')
	dict_entry_list = json.load(fin)
	fin.close()

	file_list_out = []
	
	# Go through all entries and check whether they contain any of the tags in the arg_list
	for dict_entry in dict_entry_list:
		found_total = 1
		for i in range(len(arg_list)):
			found = 0
			for tag_entry in tag_list:
				if (tag_entry in ['Place','People','tag']) and (arg_list[i] in dict_entry[tag_entry]):
					found = found+1
				elif arg_list[i] == dict_entry[tag_entry]:
					found = found+1
			found_total = found*found_total
		if found_total>0:
			filename = dict_entry['File']
			if filename[-3:] in video_suffix:
				print(filename)
				print(filename+'.THM')
			else:		
				print(filename)
	return 1

def searchPic(arg_list):
	# arg_list is a list of tags that all need to be fullfilled. 
	# the arg_list can have multiple entries like the name of people or of places
	# multiple entries will be connected with a logical AND
	# analyse the arg_list
	
	# Load the josn database with the images
	fin = open(PATH+DB_file,'r')
	dict_entry_list = json.load(fin)
	fin.close()

	file_list_out = []
	file_list_in = []
	
	if not sys.stdin.isatty():
		for line in sys.stdin:
			file_list_in.append(line[:-1])
	
	# Go through all entries and check whether they contain any of the tags in the arg_list
	for dict_entry in dict_entry_list:
		if (dict_entry['File'] in file_list_in) or (len(file_list_in)<1):
			found_total = 0
			for i in range(len(arg_list)):
				found = 0
				for tag_entry in tag_list:
					if (tag_entry in ['Place','People','tag']) and (arg_list[i] in dict_entry[tag_entry]):
						found = found+1
					elif arg_list[i] == dict_entry[tag_entry]:
						found = found+1
				found_total = found+found_total
			if found_total>0:
				filename = dict_entry['File']
				if filename[-3:] in video_suffix:
					print(filename)
					print(filename+'.THM')
				else:		
					print(filename)
	return 1

def addRemTag(dict_ent,tagCat,tag,remadd):
	# get list:
	if tagCat != 'Event':
		tag_list = dict_ent[tagCat]
		if remadd == 1:
			if not (tag in tag_list):
				tag_list.append(tag)
		elif remadd ==-1:
			if tag in tag_list:
				tag_list.remove(tag)
		dict_ent[tagCat] = tag_list
	elif tagCat == 'Event':
		if remadd == 1:
			dict_ent[tagCat] = tag
		elif remadd == -1:
			dict_ent[tagCat] = ''
	else:
		print("Error!")
		print("Not tag category: "+tagCat)
	
	return dict_ent

def changeTag(arg_list):
	# create a file list (these are the files that need to be changed)
	file_list = []
	file_found = []
	# go through the list of arguments and write out the file names. 
	for argument in arg_list:
		if (len(argument)>4) and (argument[-4] == "."):
			file_list.append(argument)
			file_found.append(0)
	
	# If no files are given as arguments, look at them in stdin
	# They can be given through a pipe.
	if len(file_list)<1:    
		if not sys.stdin.isatty():
			for line in sys.stdin:
				file_list.append(line[:-1])
				file_found.append(0)
		else:
			print("")
			print("No image file provided!")
			print("List of image files with full path needs to be provided")
			print("either as arguments, or via stdin!!\n")
			sys.exit()

	# Load the josn database with the images
	fin = open(PATH+DB_file,'r')
	dict_entry_list = json.load(fin)
	fin.close()
	i=0

	for dict_entry in dict_entry_list:
		if dict_entry['File'] in file_list:
			file_found[file_list.index(dict_entry['File'])] = 1
			tag_change = 0 # this decides, whether the next argument will be added or removed
			for argument in arg_list:
				if argument[0] == "+":
					tag_change=1
					tag_cat = argument[1:]
				elif argument[0] == '-':
					tag_change=-1
					tag_cat = argument[1:]
				elif not (argument in file_list):
					tag = argument
					temp_list = dict_entry[tag_cat]	
					dict_entry_list[i] = addRemTag(dict_entry,tag_cat,tag,tag_change)
					
		i+=1
	for i in range(len(file_list)):
		if file_found[i] == 0:
			print("File not found: "+file_list[i])

	fout = open(PATH+DB_file,'w')
	json.dump(dict_entry_list,fout,sort_keys=True,indent=2)
	fout.close()
	
	return 0

def findemptyTag(arg_list,listOutput = False):
	# Load the josn database with the images
	# if listOutput == True it only prints out the file names
	fin = open(PATH+DB_file,'r')
	dict_entry_list = json.load(fin)
	fin.close()
	i=0

	tag_list = []

	for entry in arg_list:
		if not ((len(entry)>4) and (entry[-4]==".")):
			tag_list.append(entry)

	if len(tag_list) <1:
		print('Error! - tag needs to be given as argument!')
		sys.exit(1)
	
	stopnow=1
	for dict_entry in dict_entry_list:
		for tag_entry in tag_list:
			if (len(dict_entry[tag_entry])<1)*stopnow:
				if listOutput == False: 
					print("Type \"q\" to stop!\n")
					#print(dict_entry[tag_entry])	
					#showImage(dict_entry['File'])
					filename = dict_entry['File']
					if filename[-3:] in video_suffix:
						cmd=['mpv','--loop=inf',dict_entry['File']]
					else:
						cmd=['sxiv',dict_entry['File']]
					p=subprocess.Popen(cmd)
					tag = input(tag_entry+': ')
					p.kill()
					#closeImage()
					if len(tag)<1:
						break
					if tag_entry in ['People','Place','tag']:
						if tag[0]=='q':
							stopnow = 0
							break
						for addTag in tag.split(","):
							dict_entry[tag_entry].append(addTag)
					else:
						if tag =='q':
							stopnow = 0
							break
						dict_entry[tag_entry] = tag
				else:
					try: 
						filename = dict_entry['File']
						if filename[-3:] in video_suffix:
							print(filename)
							print(filename+'.THM')
						else:	
							print(filename)
					except (BrokenPipeError, IOError):
						sys.exit()

	if listOutput == False: 
		fout = open(PATH+DB_file,'w')
		json.dump(dict_entry_list,fout,sort_keys=True,indent=2)
		fout.close()
		print("Changes saved!")	
	return 0

def singleEdit(arg_list):
	# load image database
	fin = open(PATH+DB_file,'r')
	dict_entry_list = json.load(fin)
	fin.close()
	
	# go through the files one by one and
	for dict_entry in dict_entry_list:
		if dict_entry['File'] in arg_list:
			print('')
			print(dict_entry['File'])
			print('DateTime:    '+dict_entry['DateTime'])
			print('Description: '+dict_entry['Description'])
			print('Event:       '+dict_entry['Event'])
			print('People:      [%s]'%','.join(map(str,dict_entry['People'])))
			print('Place:       [%s]'%','.join(map(str,dict_entry['Place'])))
			print('tags:        [%s]'%','.join(map(str,dict_entry['tag'])))
			print('------------------------')
			date_tag    = input('DateTime [%s]:'%dict_entry['DateTime'])
			descript    = input('Description [%s]: '%dict_entry['Description'])
			event       = input('Event [%s]: '%dict_entry['Event'])
			people_tags = input('People [%s]: '%','.join(map(str,dict_entry['People']))).split(",")
			place_tags  = input('Place [%s]: '%','.join(map(str,dict_entry['Place']))).split(",")
			tag_tags    = input('tag [%s]: '%','.join(map(str,dict_entry['tag']))).split(",")
			if len(descript)>1:
				dict_entry['Description'] = descript
			if len(event)>1:
				dict_entry['Event'] =event
			if len(date_tag) >1:
				if len(dict_entry['DateTime'])>2:
					checkagain = input("Do you really want to change the DateTime? (yes/no): ")
					if checkagain=='yes':
						dict_entry['DateTime'] = date_tag
					else:
						print('DateTime not changed!')
						print('DateTime: '+dict_entry['DateTime'] )
				dict_entry['DateTime'] = date_tag

			if len(people_tags[0])>1:
				for people_tag in people_tags:	
					if people_tag[0] == "-":
						dict_entry['People'].remove(people_tag[1:]) 
						print('Remove '+people_tag[1:])
					elif (people_tag[0] == "+") and not(people_tag[1:] in dict_entry['People']):
						dict_entry['People'].append(people_tag[1:]) 
					else:
						dict_entry['People'].append(people_tag)
			if len(place_tags[0])>1:
				for place_tag in place_tags:	
					if place_tag[0] == "-":
						dict_entry['Place'].remove(place_tag[1:]) 
					elif (place_tag[0] == "+") and not(place_tag[1:] in dict_entry['Place']):
						dict_entry['Place'].append(place_tag[1:]) 
					else:
						dict_entry['Place'].append(place_tag)
			print(tag_tags)
			if len(tag_tags[0])>1:
				for tag_tag in tag_tags:	
					if tag_tag[0] == "-":
						dict_entry['tag'].remove(tag_tag[1:]) 
					elif (tag_tag[0] == "+") and not(tag_tag[1:] in dict_entry['tag']):
						dict_entry['tag'].append(tag_tag[1:]) 
					else:
						dict_entry['tag'].append(tag_tag)
			
			print("\nUpdated:")
			print("-----------------")
			print('DateTime:    '+dict_entry['DateTime'])
			print('Description: '+dict_entry['Description'])
			print('Event:       '+dict_entry['Event'])
			print('People:      [%s]'%','.join(map(str,dict_entry['People'])))
			print('Place:       [%s]'%','.join(map(str,dict_entry['Place'])))
			print('tags:        [%s]'%','.join(map(str,dict_entry['tag'])))
			print('------------------------\n')

	fout = open(PATH+DB_file,'w')
	json.dump(dict_entry_list,fout,sort_keys=True,indent=2)
	fout.close()
	return 0

def singleShow(arg_list):
	# load image database
	fin = open(PATH+DB_file,'r')
	dict_entry_list = json.load(fin)
	fin.close()
	
	# go through the files one by one and
	for dict_entry in dict_entry_list:
		if dict_entry['File'] in arg_list:
			print('')
			print(dict_entry['File'])
			print('DateTime:    '+dict_entry['DateTime'])
			print('Description: '+dict_entry['Description'])
			print('Event:       '+dict_entry['Event'])
			print('People:      [%s]'%','.join(map(str,dict_entry['People'])))
			print('Place:       [%s]'%','.join(map(str,dict_entry['Place'])))
			print('tags:        [%s]'%','.join(map(str,dict_entry['tag'])))
			print('------------------------\n')
	return 0

def dateTime(arg_list):
	# create a file list (these are the files that need to be changed)
	date = arg_list[0]
	file_list = arg_list[1:]
	
	if len(arg_list)<2:
		print("Date and Files are needed!!")
		return 0

	# Load the josn database with the images
	fin = open(PATH+DB_file,'r')
	dict_entry_list = json.load(fin)
	fin.close()
	i=0
	print(date)
	for dict_entry in dict_entry_list:
		if dict_entry['File'] in file_list:
			dict_entry['DateTime'] = date

	fout = open(PATH+DB_file,'w')
	json.dump(dict_entry_list,fout,sort_keys=True,indent=2)
	fout.close()
	
	return 0

def sortPic(file_list):
	# get datelist for file_list
	fin = open(PATH+DB_file,'r')
	dict_entry_list = json.load(fin)
	fin.close()
	
	n_file_list = []

	for dict_entry in dict_entry_list:
		if dict_entry['File'] in file_list:
			n_file_list.append((dict_entry['DateTime'],dict_entry['File']))

	n_file_list.sort()
	for i in range(len(n_file_list)):
		filename = n_file_list[i][1]
		if filename[-3:] in video_suffix:
			print(filename)
			print(filename+'.THM')
		else:	
			print(filename)

def reversePic(file_list):
	# get datelist for file_list
	fin = open(PATH+DB_file,'r')
	dict_entry_list = json.load(fin)
	fin.close()
	
	n_file_list = []
	n_date_list = []

	for dict_entry in dict_entry_list:
		if dict_entry['File'] in file_list:
			n_file_list.append((dict_entry['DateTime'],dict_entry['File']))

	n_file_list.sort(reverse=True)

	for i in range(len(n_file_list)):
		filename = n_file_list[i][1]
		if filename[-3:] in video_suffix:
			print(filename)
			print(filename+'.THM')
		else:	
			print(filename)

def test(file_list):
	for file_entry in file_list:
		print(file_entry)	

def printArgError():
		print("Usage:\tpmanager [COMMAND] [FILE LIST]\n")
		print("Program to manage photo and video collections.")
		print("[FILE LIST] can be given as argument or via STDIN/pipe\n")
		print("Possible commands:")
		print("  update                     \n    - searches for new images and updates image database \n")
		print("  search <tags>              \n    - searches for images with tags\n")
		print("  +/-<People/Place/tag> tag <file_list>   \n    - add or remove tags \n")
		print("  findempty <tag_category>    \n    - find and displays files where no tag are given in a special category\n")
		print("  listempty <tag_category>   \n    - find and displays files where no tag are given in a special category\n")
		print("  single                     \n    - for convenient manipulation of a single image entry\n")
		print("  show <file list>           \n    - shows the entry of a list of images for convenient manipulation of a single image entry\n")
		print("  DateTime <file list>       \n    - helps you to create DateTime marks \n ")
		print("  sort             \n    - takes files from pipe (stdin) and sorts them according to their datetime from oldest to newest\n")
		print("  reverse           \n   - takes files from pipe (stdin) and sorts them according to their datetime from newest to oldest\n")
		print("  test           \n    - shows the entry of a list of images for convenient manipulation of a single image entry\n")
		#print("If no file list is given, pmanager expects file list in stdin")

####### END UPDATING ################################################################

def main():
	# first read the dict and make a backup in case something goes wrong
	try:
		fin = open(PATH+DB_file,'r')
		dict_list = json.load(fin)
		fin.close()
		fout = open(PATH+DB_file+'_backup','w')
		json.dump(dict_list,fout,sort_keys=True,indent=2)
		fout.close()
	except FileNotFoundError:
		print('Create new database file!')
	
	#parser = argparse.ArgumentParser(prog="pmanager")
#	parser.add_argument("update",help="Updates the image database. \
#	Checks for new, deleted or changed files in ~/Pictures/")
	#subparser = parser.add_subparsers()
	#parser.parse_args()

	if len(sys.argv)<2:
		printArgError()
	elif sys.argv[1] == "update":
		updateDB()	
	elif (sys.argv[1][0] == "+") or (sys.argv[1][0] == "-"):
		#Adds or removes tags to a certain image"
		changeTag(sys.argv[1:])
	elif sys.argv[1] == "search":
		#Searches for a certain image based on tags"
		searchPic(sys.argv[2:])
	elif sys.argv[1] == "findempty":
		#finds image entries where a specific tag is empty"
		findemptyTag(sys.argv[2:],listOutput=False)
	elif sys.argv[1] == "listempty":
		#finds image entries where a specific tag is empty"
		findemptyTag(sys.argv[2:],listOutput=True)
	elif sys.argv[1] == 'single':
		# Manipulates the entry of a single image"
		file_list = get_file_list(sys.argv)
		singleEdit(file_list)
	elif sys.argv[1] == 'show':
		# Shows the entry of a single image"
		file_list = get_file_list(sys.argv)
		singleShow(file_list)
	elif sys.argv[1] == 'DateTime':
		# Manipulates the entry of a single image"
		file_list = get_file_list(sys.argv)
		dateTime(file_list)
	elif sys.argv[1] == 'sort':
		file_list = get_file_list(sys.argv)
		sortPic(file_list)
	elif sys.argv[1] == 'reverse':
		file_list = get_file_list(sys.argv)
		reversePic(file_list)
	elif sys.argv[1] == 'test':
		file_list = get_file_list(sys.argv)
		test(file_list)
	else:
		printArgError()

if __name__ == "__main__":
	main()
