#!/usr/bin/env bash

cd crawler/
env GOOS=linux GOARCH=386 go build -o ../dist/linux/crawler
env GOOS=windows GOARCH=386 go build -o ../dist/windows/crawler
env GOOS=darwin GOARCH=386 go build -o ../dist/darwin/crawler