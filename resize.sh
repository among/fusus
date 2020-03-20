#!/bin/sh

book="$1"

if [[ "$book" == "" ]]; then
    echo "pass a book"
    exit
fi

if [[ ! -e "$book" ]]; then
    echo "Book $book does not exist"
    exit
fi

cd "$book"

if [[ -e inOrig ]]; then
    echo "A resize operation has already taken place"
    exit
fi

mv 'in' inOrig
mv marks marksOrig
mv dividers dividersOrig

for imsrc in 'in' marks dividers
    do
        if [[ -e $imsrc ]]; then
            rm -rf $imsrc
        fi
        mkdir $imsrc
        cd ${imsrc}Orig
        mogrify -path ../$imsrc -resize 50% *.*
        cd ..
    done
