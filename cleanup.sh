#!/bin/bash
LIMIT=2  # Upper limit

echo
echo "Removing ${LIMIT} files from directory and DB"

a=0
patt='([[:digit:]]+)'
for file in audio/*.mp3; do
	a=$(($a+1))
	if [ $a -gt "$LIMIT" ]
		then
			break
	fi
	echo "DELETING $file"
	[[ $file =~ $patt ]] && echo "${BASH_REMATCH[1]}"
	eval "python -m glitch.database delete-track ${BASH_REMATCH[1]}"
	rm $file
done
echo; echo
