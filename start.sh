#!/bin/bash

service mongodb start

env LANG=en_GB.UTF-8 mitmproxy --cadir=mitmproxy -s src/http.py
