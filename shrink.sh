#!/bin/bash
for i in *.JPG;do
	SIZE=$(stat -c%s "$i")
	if [ $SIZE -gt 3000000 ] ;
	then
		echo $i $SIZE
		convert $i -scale 75% s$i
		cp s$i $i
		rm s$i
	fi
done
