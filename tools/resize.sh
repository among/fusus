#!/bin/sh


for imsrc in 'in' marks
do
    if [[ -e ${imsrc}Orig ]]; then
        echo "A resize operation for ${imsrc} has already taken place"
    else
        echo "Resizing ${imsrc}"
        mv $imsrc ${imsrc}Orig
        if [[ -e $imsrc ]]; then
            rm -rf $imsrc
        fi
        mkdir $imsrc
        cd ${imsrc}Orig
        if [[ "$imsrc" == "in" ]]; then
            mogrify -path ../$imsrc -resize 50% *.*
        else
            for subdir in *
            do
                echo "Resizing $imsrc/$subdir"
                mkdir ../$imsrc/$subdir
                cd $subdir
                mogrify -path ../../$imsrc/$subdir -resize 50% *.*
                cd ..
            done
        fi
            
        cd ..

    fi
done
