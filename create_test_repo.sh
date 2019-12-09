#!/bin/bash

set -o nounset
set -o errexit
set -o pipefail

TESTREPO="testrepo"

rm -rf "$TESTREPO"

git init "$TESTREPO"
pushd "$TESTREPO"

echo -e "aaa\n" > a.txt
git add a.txt
git commit -m "Commit 1" -m "- added a.txt"

echo -e "BBB\n" > b.txt
git add b.txt
git commit -m "Commit 2" -m "- added b.txt" -s

popd
