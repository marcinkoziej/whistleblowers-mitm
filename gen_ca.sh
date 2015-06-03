#!/bin/bash

echo "Generating cert for ${1:-1} days"  >&2

openssl genrsa -out mitmproxy/ca.key 1024

openssl req -new -x509 -days ${1:-1} -key mitmproxy/ca.key -out mitmproxy/ca.crt -subj /CN=Whistleblowers\ Workshop/OU=Radiofonia
cat mitmproxy/ca.key mitmproxy/ca.crt > mitmproxy/mitmproxy-ca.pem
