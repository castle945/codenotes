#!/bin/bash
# Install Robot Operating System (ROS) on NVIDIA Jetson AGX Xavier
# ref https://github.com/dusty-nv/jetson-containers/blob/master/Dockerfile.ros.melodic
# tested on Jetpack 4.6.2

# FROM nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3
# FROM nvcr.io/nvidia/l4t-base:r32.7.1

apt update && \
apt-get install -y --no-install-recommends sudo git cmake build-essential curl wget gnupg2 lsb-release ca-certificates

# Setup sources.lst
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
# Setup keys
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc && \
cat ros.asc | apt-key add -

sudo apt-get update
sudo apt-get install ros-melodic-desktop-full
sudo apt install -y python-rosdep python-rosinstall python-rosinstall-generator python-wstool

rm -rf /var/lib/apt/lists/*

# Initialize rosdep 
# https://blog.csdn.net/qq_41426807/article/details/125376373
# git clone https://github.com/ros/rosdistro.git ~/Desktop/

sudo sed -i "s#https://raw.githubusercontent.com/ros/rosdistro/master#file:///${HOME}/Desktop/rosdistro#g" /usr/lib/python2.7/dist-packages/rosdep2/main.py
sudo sed -i "s#https://raw.githubusercontent.com/ros/rosdistro/master#file:///${HOME}/Desktop/rosdistro#g" /usr/lib/python2.7/dist-packages/rosdep2/rep3.py
sudo sed -i "s#https://raw.githubusercontent.com/ros/rosdistro/master#file:///${HOME}/Desktop/rosdistro#g" /usr/lib/python2.7/dist-packages/rosdistro/__init__.py
sudo sed -i "s#https://raw.githubusercontent.com/ros/rosdistro/master#file:///${HOME}/Desktop/rosdistro#g" /usr/lib/python2.7/dist-packages/rosdep2/sources_list.py

sudo rosdep init

sudo sed -i "s#https://raw.githubusercontent.com/ros/rosdistro/master#file:///${HOME}/Desktop/rosdistro#g" /etc/ros/rosdep/sources.list.d/20-default.list

rosdep update

echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
echo "source /opt/ros/melodic/setup.bash" >> ~/.zshrc
