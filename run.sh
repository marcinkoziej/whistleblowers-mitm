#!/bin/bash
exec docker run --rm -ti -v `pwd`/src:/usr/app/src -p 8080:8080 -p 27017:27017 --name mitm whistleblowers/mitm
