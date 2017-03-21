#!/bin/bash

DEST=/var/www/html/autoconfig.momo
TEMP=/var/www/html/autoconfig-temp
DATA=/var/www/autoconfig.momo
cd $DATA
rm -rf convert.py
wget https://svn.mozilla.org/mozillamessaging.com/sites/ispdb.mozillamessaging.com/trunk/tools/convert.py
cd $DATA/trunk
git fetch --all
git checkout --force origin/prod

# Make sure we regenerate all the files so deleted files don't stay.

mkdir -p $TEMP
mkdir -p $TEMP/v1.1
mkdir -p $TEMP/v1.0

source /var/www/tbservices/bin/activate
python ../convert.py -a -d $TEMP/v1.1 *
rm -rf $DATA/trunk/cloudnine-net.jp
python ../convert.py -a -d $TEMP/v1.0 -v 1.0 *

rm -rf $DEST
mv $TEMP $DEST
