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

When I realised the power of feh, I decided to use feh for my image handling. I wrote the image
information in a json-database. Now the database can easily manipulated with simple tools.

# pmanager

## Install
Download the zip file or clone the git repository

```git clone https://github.com/steview2000/pManager.git```

Enter the created directory and install the main program
```cd pManager
   python setup.py install
```

This will install the main program (pManager). However, the scripts checkImage, kPhoto2Pmanager.py,
and pmanager_direct shall be placed by hand somewhere else like in a bin directory, or directly where
they will be used.


## Usage

```pmanager <option> <argument> <file>```

Depending on the option, you can either add arguments or not.

#### Updating the database

```pmanager update```

This updates the data base. pmanager search for new or deleted files in ~/Pictures and changes the
database accordingly. If possible date and times are taken from the exif-informations of the image.
Data are stored in imageDB.json

#### Adding or removing tags
There are three different tag-categories:

	- People: for the people
	- Place:  for the locations
	- tag:	  for all other tags

Tags can be added or removed to any of these three categories like this
```pmanager +People Hanns Sarah John -People Julia +Place Germany file1.jpg file2.jpg```

This adds to eacho of the images file1.jpg and file2.jpg the People tag Hanns, Sarah, and John, and
removes Julia and adds the Place-tag Germany.




	


