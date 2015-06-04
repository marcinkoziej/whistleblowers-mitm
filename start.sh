#!/bin/bash

if [[ `id -u` > 0 ]]; then echo "I need root"; exit 1; fi

echo "set up PF to hijack connections"
pfctl -a com.apple.internet-sharing/base_v4 -f /etc/pf.mitm.conf


echo "have python env activated"
. env/bin/activate

if [[ ! `pgrep mongod` > 0 ]]; then
  echo "run as user mongodb with: mongod --config /usr/local/etc/mongod.conf"
fi

echo "adding `pwd`/src to PYTHONPATH"
export PYTHONPATH=`pwd`/src:$PYTHONPATH
echo "Offblast!"
mitmdump -T --host --cadir=mitmproxy -s src/http.py
