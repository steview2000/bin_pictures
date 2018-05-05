import xml.etree.ElementTree as ET
tree = ET.parse('index.xml')
root = tree.getroot()

# list of filenames
tag_list = []
file_list = []
tag_saved = []

for child in root.iter('image'):
	filename = child.get('file')
	print('/home/stevie/Pictures/'+filename)

	for option in child.iter('option'):
		category = option.get('name')
		#print(category)

		for subcat in option.iter('value'):
			imtag = subcat.get('value')
			#print(subcat.get('value'))
			tag = category+"_"+imtag
			print(tag)
			tag_list.append(tag.replace(' ','_').replace('/','-'))
			file_list.append('/home/stevie/Pictures/'+filename)

N = len(tag_list)

for i in range(N):
	if not(tag_list[i] in tag_saved):
		tag_saved.append(tag_list[i])
		print(tag_list[i])
		fTag = open('/home/stevie/.local/share/vimiv/Tags/'+tag_list[i],'a')
	
		for j in range(N):
			if tag_list[j] == tag_list[i]:
				fTag.write(file_list[j]+'\n')
		fTag.close()
	


