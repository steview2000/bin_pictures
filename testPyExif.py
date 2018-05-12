import exifread

f = open('/home/stevie/Pictures/PicForAnnita/guyl0001.JPG','rb')
tags = exifread.process_file(f)

