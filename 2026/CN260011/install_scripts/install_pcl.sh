#!/bin/bash

# # ! 注意，ubuntu20.04阿里云源安装libpcl-dev会出错，部分依赖 Undetermined Error [IP:
sudo sed -i 's/mirrors.aliyun.com/archive.ubuntu.com/g' /etc/apt/sources.list 
sudo apt update; sudo apt upgrade -y; sudo apt autoremove          
# sudo apt install -y libpcl-dev pcl-tools 

###############################################################################
#
#  最新版 pcl
#
###############################################################################

# # https://github.com/PointCloudLibrary/pcl/blob/master/.dev/docker/release/Dockerfile
# # ! 注意，ubuntu20.04阿里云源安装libpcl-dev会出错，部分依赖 Undetermined Error [IP:
# sudo sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list 
# sudo apt update; sudo apt upgrade -y; sudo apt autoremove          

VTK_VERSION=7
PCL_INDEX_SIGNED=true
PCL_INDEX_SIZE=32

# Add sources so we can just install build-dependencies of PCL
# sed 's/^deb \(.*\)$/deb \1\ndeb-src \1/' /etc/apt/sources.list # 解注释放开一些源码源
sudo sed -i 's/^deb \(.*\)$/deb \1\ndeb-src \1/' /etc/apt/sources.list \
 && sudo apt update \
 && sudo apt install -y \
    bash \
    cmake \
    dpkg-dev \
    git \
    g++ \
    libboost-date-time-dev \
    libboost-filesystem-dev \
    libboost-iostreams-dev \
    libeigen3-dev \
    libflann-dev \
    libglew-dev \
    libgtest-dev \
    libopenni-dev \
    libopenni2-dev \
    libproj-dev \
    libqhull-dev \
    libqt5opengl5-dev \
    libusb-1.0-0-dev \
    libvtk${VTK_VERSION}-dev \
    libvtk${VTK_VERSION}-qt-dev \
    qtbase5-dev \
    wget \
 && sudo rm -rf /var/lib/apt/lists/*

# CMake flags are from dpkg helper
# PCL config is from debian repo:
# https://salsa.debian.org/science-team/pcl/-/blob/master/debian/rules
# MinSizeRel is used for the CI and should have no impact on releaseability
cd \
 && git clone --depth=1 https://github.com/PointCloudLibrary/pcl \
 && mkdir pcl/build \
 && cd pcl/build \
 && export DEB_BUILD_MAINT_OPTIONS='hardening=+all' \
 && export DEB_CFLAGS_MAINT_APPEND="-Wall -pedantic" \
 && export DEB_LDFLAGS_MAINT_APPEND="-Wl,--as-needed" \
 && cmake .. \
    -DCMAKE_BUILD_TYPE=MinSizeRel \
    -DCMAKE_CXX_FLAGS:STRING="`dpkg-buildflags --get CXXFLAGS`"          \
    -DCMAKE_EXE_LINKER_FLAGS:STRING="`dpkg-buildflags --get LDFLAGS`"    \
    -DCMAKE_SHARED_LINKER_FLAGS:STRING="`dpkg-buildflags --get LDFLAGS`" \
    -DCMAKE_SKIP_RPATH=ON -DPCL_ENABLE_SSE=OFF                          \
    -DBUILD_TESTS=OFF -DBUILD_apps=ON -DBUILD_common=ON                 \
    -DBUILD_examples=ON -DBUILD_features=ON -DBUILD_filters=ON           \
    -DBUILD_geometry=ON -DBUILD_global_tests=OFF -DBUILD_io=ON          \
    -DBUILD_kdtree=ON -DBUILD_keypoints=ON -DBUILD_octree=ON            \
    -DBUILD_registration=ON -DBUILD_sample_consensus=ON                 \
    -DBUILD_search=ON -DBUILD_segmentation=ON -DBUILD_surface=ON        \
    -DBUILD_tools=ON -DBUILD_tracking=ON -DBUILD_visualization=ON       \
    -DBUILD_apps_cloud_composer=OFF -DBUILD_apps_modeler=ON             \
    -DBUILD_apps_point_cloud_editor=ON -DBUILD_apps_in_hand_scanner=ON  \
    -DPCL_INDEX_SIGNED=${PCL_INDEX_SIGNED} \
    -DPCL_INDEX_SIZE=${PCL_INDEX_SIZE} \
    -DBUILD_GPU=ON \
 && make -j8 \
 && sudo make install \
 && cd \
 && rm -fr pcl

# 注释放下面，不能上一行不能右边，\尾部还不许有空格
# 自定义选项
# -DBUILD_GPU=ON # 编译GPU模块，从而可以 pcl cuda 混合编程