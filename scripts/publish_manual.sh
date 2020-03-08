#!/bin/sh
cd manual
asciidoctor index.adoc
rm -rf yamlfu.github.io
git clone  --depth 1 git@github.com:yamlfu/yamlfu.github.io.git
cp index.html yamlfu.github.io
cd yamlfu.github.io
git add index.html
git commit -m "$1"
git push