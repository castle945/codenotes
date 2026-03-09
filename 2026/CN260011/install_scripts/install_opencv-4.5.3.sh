#!/bin/bash
url="https://github.com/opencv/opencv/archive/refs/tags/4.5.3.tar.gz"
name="opencv-4.5.3"

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
