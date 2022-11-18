#!/bin/bash

DEST=/var/www/html/autoconfig.momo
# move files here to be deleted, just cause mv is faster than rm
PURGEDIR=/var/www/html/autoconfig-purge
# we generate the files in the temp dir first and then move into place to avoid temporary 404s
TEMP=/var/www/html/autoconfig-temp
DATA=/var/www/autoconfig.momo/ispdb

# Make sure we regenerate all the files so deleted files don't stay.
mkdir -p $TEMP
mkdir -p $TEMP/v1.1

cd $DATA
cp -R ../webroot/* $TEMP
source /var/www/tbservices/bin/activate
python ../tools/convert.py -a -d $TEMP/v1.1 *

mv $DEST $PURGEDIR
mv $TEMP $DEST
rm -rf $PURGEDIR
