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

#TODO: Add the path of the whole file, when not given otherwise

PATH = os.path.expanduser('~')+'/Pictures/' # this is the path for the images

# Database file
DB_file = 'imageDB.json'

# possible tags
tag_list = ['DateTime','ID','People','Place','Event','tag']

def get_date_taken(path):
	#print(path)
	# first try the pure python way
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

	return dateCreate

def calcID(path):
	# this functions generates a unique imageID based on the md5sum hash
	f = open(path,'rb')
	id_f = hashlib.md5(f.read()).hexdigest()
	f.close()
	return id_f

def showImage(filename):
	cmd=['feh','-.','-b','black','--draw-exif','--draw-tinted',filename]
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
		
		if file_count%200==0:	
			print(("completed: %i/%i")%(file_count,N_file))
		
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
		if exist_already ==0:
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
	
	# Go through all entries and check whether they contain all of the tags in the arg_list
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
			print(dict_entry['File'])
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

def findemptyTag(arg_list):
	# Load the josn database with the images
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
				print("Type \"q\" to stop!\n")
				#print(dict_entry[tag_entry])	
				#showImage(dict_entry['File'])
				cmd=['feh','-.','-b','black','--draw-exif','--draw-tinted',dict_entry['File']]
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

def test(file_list):
	for file_entry in file_list:
		print(file_entry)	

def printArgError():
		print("Usage:\tpmanager <option> <file list>\n")
		print("Possible options:")
		print("update                     - searches for new images and updates image database ")
		print("search <tags>              - searches for images with tags")
		print("+/-<People/Place/tag> tag  - tags of the categories People/Place/tag are added or removed ")
		print("findempty <tag_category>   - find and displays files where no tag are given in a\
		special category")
		print("single                     - for convenient manipulation of a single image entry")
		print("show <file list>           - shows the entry of a list of images for convenient manipulation of a single image entry")

####### END UPDATING ################################################################

def main():
	# first read the dict and make a backup
	try:
		fin = open(PATH+DB_file,'r')
		dict_list = json.load(fin)
		fin.close()
		fout = open(PATH+DB_file+'_backup','w')
		json.dump(dict_list,fout,sort_keys=True,indent=2)
		fout.close()
	except FileNotFoundError:
		print('Create new database file!')
	
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
		findemptyTag(sys.argv[2:])
	elif sys.argv[1] == 'single':
		# Manipulates the entry of a single image"
		singleEdit(sys.argv[2:])
	elif sys.argv[1] == 'show':
		# Manipulates the entry of a single image"
		singleShow(sys.argv[2:])
	elif sys.argv[1] == 'DateTime':
		# Manipulates the entry of a single image"
		dateTime(sys.argv[2:])
	elif sys.argv[1] == 'test':
		test(sys.argv[2:])
	else:
		printArgError()

if __name__ == "__main__":
	main()
