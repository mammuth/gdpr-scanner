#!/usr/bin/env bash

cd crawler/
#env GOOS=darwin GOARCH=386 go build -o ../build/darwin/crawler
env GOOS=linux GOARCH=386 go build -o ../build/linux/crawler

scp ../build/linux/crawler root@box.maxi-muth.de:/root/gdpr-scanner/crawler