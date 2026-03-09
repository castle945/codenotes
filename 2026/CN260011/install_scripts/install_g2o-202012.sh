#!/bin/bash
# url="https://github.com/RainerKuemmerle/g2o/archive/refs/tags/20200410_git.tar.gz"
# name="g2o-202004"
url="https://github.com/RainerKuemmerle/g2o/archive/refs/tags/20201223_git.tar.gz"
name="g2o-202012"

pkg_dir="${HOME}/.local/lib"
cd ; wget -O ${name}.tar.gz $url && \
mkdir ${name}; tar -zxvf ${name}.tar.gz -C ${name} --strip-components 1 && \
cd ${name}; mkdir build ; cd build && \
cmake -DCMAKE_BUILD_TYPE=RELEASE \
        -DCMAKE_INSTALL_PREFIX=${pkg_dir}/${name}/installed \
        .. && \
make -j8 && \
make install && \
cd ; rm -rf ${name}.tar.gz ${name} && \
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:${pkg_dir}/${name}/installed/lib" >> ~/.zshrc