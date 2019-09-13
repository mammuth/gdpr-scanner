#!/usr/bin/env bash

printf "Go Lines Of Code\n"
find . -name '*.go' | xargs wc -l

printf "\n"

printf "Python Lines Of Code\n"
find . -name '*.py' | xargs wc -l