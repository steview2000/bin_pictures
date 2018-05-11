#!/bin/bash
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

create_date="$(exiftool "$1"|grep "Time Original" |head -1|awk -F" " '{print $4, $5}')"
#exiftool "$1"|grep "sime Original" |head -1|awk -F" " '{print $4, $5}'

#echo $create_date

if [ -z "$create_date" ];then
	#echo "not found"
	create_date="$(exiftool "$1"|grep "Content Create Date" |head -1|awk -F" " '{print $5, $6}')"
fi

echo $create_date
# restore $IFS
IFS=$SAVEIFS
