This repository contains usefull scripts and programs to manage photos, pictures and videos in ~/Pictures

# Why

I have some pictures and I wanted to sort them in some way. After trying out a few photomanagers
(digikam,  geeqie, shotwell), I finally settled with kPhotoAlbum. It was exactly, what I needed:
	
 - doesn't change location of the files on the hard drive
 - tagging was possible
 - tagging into categories was possible
 - very nice graphical user interface

However, there were a few things that I found annoying:

 - Handling of videos was annoying (no thumbnails for many of them)
 - kPhotoalbum always demanded mplayer2, while I had installed mplayer or mpv (mplayer2 was slow when I tried it), therefore there was no automatic video playing
 - Tagging images and many operations where mouse driven and therefore quite slow
 - The image database is saved as an .xml file. I find .xml files often quite confusing

When I realised the power of sxiv, I decided to use sxiv for my image handling. I wrote the image
information in a json-database. Now the database can easily manipulated with simple tools.

# The image database
Information of the images are stored in a json database (~/Pictures/imageDB.json). For each image,
there are following entries:
 - ID:	 		a unique ID for each image (the md5 checksum of the corresponding file)
 - File: 		the file name and location of the image 
 - Description: A description about the image
 - DateTime:	The date and time when the image was taken
 - Event:		The event at which the image was taken (e.g., vacation in Colorado)
 - Place:		The place at which the image was taken 
 - People:		People on the picture
 - tag:			Other tags

# pmanager
This is the main program, which manages a json-image database (~/Pictures/imageDB.json). 


## Dependencies:
 - sxiv (https://github.com/muennich/sxiv)
 - exiftool (https://sno.phy.queensu.ca/~phil/exiftool/)
 - mpv (https://github.com/mpv-player/mpv)

## Install
Install the dependencies first. Under debian/Ubuntu or Mint:

```sudo apt-get sxiv exiftool mpv```

Download the zip file or clone the git repository

```git clone https://github.com/steview2000/pManager.git```

Enter the created directory and install the main program

```
cd pManager
python setup.py install
```

This will install the main program (pManager). However, the scripts checkImage, kPhoto2Pmanager.py,
and pmanager_direct shall be placed by hand somewhere else like in a bin directory, or directly where
they will be used.


## Usage

```pmanager <option> <argument> <file>```

Depending on the option, you can either add arguments or not. Below are the possible options.

#### Updating the database

```pmanager update```

This updates the data base. pmanager searches for new or deleted files in ~/Pictures and changes the
database accordingly. If possible, dates and times are taken from the exif-informations of the image.
Also, if files are renamed or moved to a different location, pmanager edits the image database
accordingly. Data are stored in ~/Pictures/imageDB.json

#### Adding or removing tags
There are three different tag-categories:

 - People: for the people
 - Place:  for the locations
 - tag:	  for all other tags

Tags can be added or removed to any of these three categories like this
```pmanager +People Hanns Sarah John -People Julia +Place Germany file1.jpg file2.jpg```

This adds to eacho of the images file1.jpg and file2.jpg the People tag Hanns, Sarah, and John, and
removes Julia and adds the Place-tag Germany.

#### Search for certain tags

```pmanager search tag1 tag2 tag3```

This search for images that have tag1, tag2, and tag3 in them. This function does not differentiate
whether the tags are people, places or other common tags. If multiple takes are given (as in the
example) images are shown, where all thes tags are present (AND operation). The function returns the
full paths of the images.

#### Show image information

```pmanager show <filename>```

This functions shows the information about a single image file. Here <filename> must be the full
path to a file.

#### Edit entry of a single image

```pmanager single <filename>```

This lets you edit the entries for a single image. Here filename is the full path and filename of an
image.

#### Find untagges images

```pmanager findempty <tag-category>```

This function finds and shows images that have not been tagged yet in a specific tag-category.


	


