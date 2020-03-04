#!/bin/sh
cd manual
asciidoctor index.adoc
rm -rf yamlpy.github.io
git clone  --depth 1 git@github.com:YAMLPy/yamlpy.github.io.git
cp index.html yamlpy.github.io
cd yamlpy.github.io
git add index.html
git commit -m "$1"
git push