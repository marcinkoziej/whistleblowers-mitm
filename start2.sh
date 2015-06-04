#!/bin/bash



echo "have python env activated"
. env/bin/activate

if [[ ! `pgrep mongod` > 0 ]]; then
  echo "run as user mongodb with: mongod --config /usr/local/etc/mongod.conf"
fi

echo "adding `pwd`/src to PYTHONPATH"
export PYTHONPATH=`pwd`/src:$PYTHONPATH
echo "Offblast!"
mitmdump --cadir=mitmproxy -s src/http.py
