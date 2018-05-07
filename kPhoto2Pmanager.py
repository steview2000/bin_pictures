import xml.etree.ElementTree as ET
import pmanager
import os

PATH = os.path.expanduser('~')+'/Pictures/' # this is the path for the images
DB_file = PATH+'imageDB.json'
tree = ET.parse(PATH+'index.xml')
root = tree.getroot()

# list of filenames
tag_list = []
file_list = []
tag_saved = []

try:
	fin = open(PATH+DB_file,'r')
	dict_list = json.load(fin)
	fin.close()
except FileNotFoundError:
	dict_list = []

for child in root.iter('image'):
	filename = child.get('file')
	print(PATH+filename)
	cmdList = []
	for option in child.iter('option'):
		category = option.get('name')
		#print(category)
		if category == 'People':
			cmdList.append('+People')
		elif category == 'Places':
			cmdList.append('+Place')
		elif category=='Tokens':
			"I don't care about Tokens!"
		else:
			cmdList.append('+tag')

		for subcat in option.iter('value'):
			imtag = subcat.get('value')
			if (len(imtag)>1) and (imtag != 'untagged'):
				#print(imtag)
				#print(cmdList)
				cmdList.append(imtag)
			#print(subcat.get('value'))

	cmdList.append(PATH+filename)	
	pmanager.changeTag(cmdList)

