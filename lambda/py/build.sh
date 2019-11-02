#!/usr/bin/env bash
rm build.zip
mkdir -p build
docker run --rm -v $(pwd):/var/task lambci/lambda:build-python3.7 python3.7 -m pip install -t /var/task/build -r requirements.txt
cp -r .parallelcluster parallel_cluster.py build
mv build/bin/pcluster build/pcluster-cli
cd build
rm -rf enum enum34*
zip -r -9 ../build.zip * .libs_cffi_backend .parallelcluster
cd ..
rm -r build
